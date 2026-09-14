# """Orchestration métier du cycle de vie d'un dossier persisté.

# Fait le lien entre la persistance (repositories) et le système expert
# stateless existant (backend.services.expert_service, non modifié -
# CONCEPTION_V2.md interdit de toucher au moteur de règles). Ce service ne
# contient aucune règle métier : il charge l'état, appelle le moteur existant,
# persiste le résultat.

# MODIFICATION (Problème 1 — redondance PieceJustificative) : les 5 booléens
# autrefois portés directement par Dossier sont désormais lus/écrits via
# PieceJustificative (_piece_fournie), source de vérité unique.

# MODIFICATION (Problème 6 — statut hors périmètre) : evaluer_et_persister
# marque le dossier HORS_PERIMETRE_AUTOMATISE plutôt que EVALUE si l'apport
# (global ou par associé) est en nature.

# MODIFICATION (visibilité des associés + anti-doublon) : _construire_dossier_read
# expose désormais la liste des associés déjà enregistrés (DossierRead.identites),
# et ajouter_identite refuse un numéro CIN déjà présent pour ce dossier.

# MODIFICATION (admin lecture seule) : ajout de lister_tous_admin et
# obtenir_dossier_admin — réutilisent _construire_dossier_read telle quelle.
# """

# from __future__ import annotations

# import uuid

# from sqlalchemy.orm import Session

# from backend.core.exceptions import DossierIntrouvableError, IdentiteDupliqueeError
# from backend.models.dossier import Dossier
# from backend.models.enums import StatutGlobalEnum, TypePieceEnum
# from backend.repositories.dossier_repository import DossierRepository
# from backend.repositories.evaluation_repository import EvaluationRepository
# from backend.schemas.admin import DossierAdminRead
# from backend.schemas.dossier import (
#     DossierCreate,
#     DossierInput,
#     DossierRead,
#     DossierUpdate,
#     IdentitePersonneInput,
#     IdentitePersonneRead,
#     PieceJustificativeInput,
# )
# from backend.schemas.evaluation import AnomalieResult, EvaluationRead, VerdictDossier
# from backend.services.expert_service import evaluer_dossier


# from sqlalchemy.exc import IntegrityError

# from backend.core.exceptions import (
#     DossierIntrouvableError,
#     IdentiteDupliqueeError,
#     IdentiteIntrouvableError,
# )
# from backend.schemas.dossier import (
#     DossierCreate,
#     DossierInput,
#     DossierRead,
#     DossierUpdate,
#     IdentitePersonneInput,
#     IdentitePersonneRead,
#     IdentitePersonneUpdate,
#     PieceJustificativeInput,
# )


# _NB_CHAMPS_PROGRESSION = 5


# def _piece_fournie(dossier: Dossier, type_piece: str) -> bool:
#     """Point d'accès unique pour savoir si une pièce est fournie — les
#     règles du système expert et la construction de DossierRead passent
#     toutes par ici plutôt que de lire un booléen dupliqué sur Dossier."""
#     return any(p.type_piece == type_piece and p.fournie for p in dossier.pieces)


# def _obtenir_dossier_ou_404(
#     db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID
# ) -> Dossier:
#     dossier = DossierRepository(db).obtenir(dossier_id, entrepreneur_id)
#     if dossier is None:
#         raise DossierIntrouvableError("Dossier introuvable.")
#     return dossier


# def creer_dossier(db: Session, entrepreneur_id: uuid.UUID, payload: DossierCreate) -> DossierRead:
#     dossier = DossierRepository(db).creer(entrepreneur_id, payload)
#     return _construire_dossier_read(db, dossier)


# def lister_dossiers(db: Session, entrepreneur_id: uuid.UUID) -> list[DossierRead]:
#     dossiers = DossierRepository(db).lister_pour_utilisateur(entrepreneur_id)
#     return [_construire_dossier_read(db, dossier) for dossier in dossiers]


# def obtenir_dossier(db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID) -> DossierRead:
#     dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
#     return _construire_dossier_read(db, dossier)


# def mettre_a_jour_dossier(
#     db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID, payload: DossierUpdate
# ) -> DossierRead:
#     dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
#     dossier = DossierRepository(db).mettre_a_jour(dossier, payload)
#     return _construire_dossier_read(db, dossier)


# def ajouter_identite(
#     db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID, payload: IdentitePersonneInput
# ) -> DossierRead:
#     dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)

#     DossierRepository(db).ajouter_identite(dossier, payload)
#     return _construire_dossier_read(db, dossier)


# def lister_evaluations(
#     db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID
# ) -> list[EvaluationRead]:
#     _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
#     evaluations = EvaluationRepository(db).lister_pour_dossier(dossier_id)
#     return [
#         EvaluationRead(
#             id=str(e.id),
#             date_evaluation=e.date_evaluation,
#             statut_global=StatutGlobalEnum(e.statut_global),
#             anomalies=[
#                 AnomalieResult(
#                     id=str(a.id),
#                     regle_id=a.regle_id,
#                     categorie=a.categorie,
#                     gravite=a.gravite,
#                     message=a.message,
#                     justification=a.justification,
#                     reference_documentaire=a.reference_documentaire,
#                     niveau_documentaire=a.niveau_documentaire,
#                 )
#                 for a in e.anomalies
#             ],
#         )
#         for e in evaluations
#     ]


# def evaluer_et_persister(
#     db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID
# ) -> EvaluationRead:
#     dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)

#     dossier_input = DossierInput(
#         forme_juridique=dossier.forme_juridique,
#         capital_social=float(dossier.capital_social),
#         siege_social=dossier.siege_social,
#         statuts_fournis=_piece_fournie(dossier, TypePieceEnum.STATUTS.value),
#         attestation_blocage_bancaire_fournie=_piece_fournie(
#             dossier, TypePieceEnum.ATTESTATION_BLOCAGE_BANCAIRE.value
#         ),
#         emploie_salaries=dossier.emploie_salaries,
#         type_justificatif_siege=dossier.type_justificatif_siege,
#         gerant_designe_dans_statuts=dossier.gerant_designe_dans_statuts,
#         identites=[
#             IdentitePersonneInput(
#                 nom=i.nom or "",
#                 prenom=i.prenom or "",
#                 numero_cin=i.numero_cin or "",
#                 date_naissance=i.date_naissance,
#                 type_apport_personnel=i.type_apport_personnel,
#                 montant_apport=float(i.montant_apport) if i.montant_apport is not None else None,
#             )
#             for i in dossier.identites
#         ],
#         pieces=[
#             PieceJustificativeInput(type_piece=p.type_piece, fournie=p.fournie)
#             for p in dossier.pieces
#         ],
#     )

#     verdict: VerdictDossier = evaluer_dossier(dossier_input)

#     evaluation = EvaluationRepository(db).creer(dossier.id, verdict)

#     apport_en_nature = dossier.type_apport == "nature" or any(
#         i.type_apport_personnel == "nature" for i in dossier.identites
#     )
#     if apport_en_nature:
#         DossierRepository(db).marquer_hors_perimetre(dossier)
#     else:
#         DossierRepository(db).marquer_evalue(dossier)

#     return EvaluationRead(
#         id=str(evaluation.id),
#         date_evaluation=evaluation.date_evaluation,
#         statut_global=verdict.statut_global,
#         anomalies=verdict.anomalies,
#     )


# def lister_tous_admin(db: Session) -> list[DossierAdminRead]:
#     dossiers = DossierRepository(db).lister_tous()
#     return [
#         DossierAdminRead(
#             dossier=_construire_dossier_read(db, dossier),
#             entrepreneur_nom=dossier.entrepreneur.nom,
#             entrepreneur_email=dossier.entrepreneur.email,
#         )
#         for dossier in dossiers
#     ]


# def obtenir_dossier_admin(db: Session, dossier_id: uuid.UUID) -> DossierAdminRead:
#     dossier = DossierRepository(db).obtenir_par_id(dossier_id)
#     if dossier is None:
#         raise DossierIntrouvableError("Dossier introuvable.")
#     return DossierAdminRead(
#         dossier=_construire_dossier_read(db, dossier),
#         entrepreneur_nom=dossier.entrepreneur.nom,
#         entrepreneur_email=dossier.entrepreneur.email,
#     )


# def _construire_dossier_read(db: Session, dossier: Dossier) -> DossierRead:
#     derniere = EvaluationRepository(db).derniere_pour_dossier(dossier.id)

#     nb_bloquantes = 0
#     nb_avertissements = 0
#     pret_pour_depot = False
#     date_derniere_evaluation = None

#     if derniere is not None:
#         date_derniere_evaluation = derniere.date_evaluation
#         nb_bloquantes = sum(1 for a in derniere.anomalies if a.gravite == "bloquante")
#         nb_avertissements = sum(
#             1 for a in derniere.anomalies if a.gravite in ("avertissement", "informative")
#         )
#         pret_pour_depot = derniere.statut_global in (
#             StatutGlobalEnum.CONFORME,
#             StatutGlobalEnum.CONFORME_AVEC_RESERVES,
#         )

#     champs_remplis = sum(
#         [
#             bool(dossier.nom_projet),
#             bool(dossier.forme_juridique),
#             dossier.capital_social is not None and float(dossier.capital_social) > 0,
#             bool(dossier.siege_social),
#             len(dossier.identites) > 0,
#         ]
#     )


#     progression_pct = round(100 * champs_remplis / _NB_CHAMPS_PROGRESSION)

#     return DossierRead(
#         id=str(dossier.id),
#         nom_projet=dossier.nom_projet,
#         forme_juridique=dossier.forme_juridique,
#         capital_social=float(dossier.capital_social),
#         siege_social=dossier.siege_social,
#         statuts_fournis=_piece_fournie(dossier, TypePieceEnum.STATUTS.value),
#         # certificat_negatif_fourni=_piece_fournie(dossier, TypePieceEnum.CERTIFICAT_NEGATIF.value),
#         # certificat_negatif_date_delivrance=dossier.certificat_negatif_date_delivrance,
#         attestation_blocage_bancaire_fournie=_piece_fournie(
#             dossier, TypePieceEnum.ATTESTATION_BLOCAGE_BANCAIRE.value
#         ),
#         # taxe_professionnelle_declaree=_piece_fournie(dossier, TypePieceEnum.TAXE_PROFESSIONNELLE.value),
#         emploie_salaries=dossier.emploie_salaries,
#         # affiliation_cnss_fournie=_piece_fournie(dossier, TypePieceEnum.AFFILIATION_CNSS.value),
#         type_justificatif_siege=dossier.type_justificatif_siege,
#         gerant_designe_dans_statuts=dossier.gerant_designe_dans_statuts,
#         statut=dossier.statut,
#         date_creation=dossier.date_creation,
#         progression_pct=progression_pct,
#         nb_erreurs_bloquantes=nb_bloquantes,
#         nb_avertissements=nb_avertissements,
#         pret_pour_depot=pret_pour_depot,
#         date_derniere_evaluation=date_derniere_evaluation,
#         identites=[
#             IdentitePersonneRead(
#                 id=str(i.id),
#                 nom=i.nom,
#                 prenom=i.prenom,
#                 numero_cin=i.numero_cin,
#                 date_naissance=i.date_naissance,
#                 type_apport_personnel=i.type_apport_personnel,
#                 montant_apport=float(i.montant_apport) if i.montant_apport is not None else None,
#             )
#             for i in dossier.identites
#         ],
#     )


# def modifier_identite(
#     db: Session,
#     dossier_id: uuid.UUID,
#     entrepreneur_id: uuid.UUID,
#     identite_id: uuid.UUID,
#     payload: IdentitePersonneUpdate,
# ) -> DossierRead:
#     dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
#     identite = DossierRepository(db).obtenir_identite(dossier_id, identite_id)
#     if identite is None:
#         raise IdentiteIntrouvableError("Associé introuvable pour ce dossier.")

#     if payload.numero_cin and any(
#         i.numero_cin == payload.numero_cin and i.id != identite_id for i in dossier.identites
#     ):
#         raise IdentiteDupliqueeError(
#             f"Un associé avec le numéro CIN {payload.numero_cin} existe déjà pour ce dossier."
#         )

#     try:
#         DossierRepository(db).mettre_a_jour_identite(identite, payload)
#     except IntegrityError as exc:
#         db.rollback()
#         raise IdentiteDupliqueeError(
#             f"Un associé avec le numéro CIN {payload.numero_cin} existe déjà pour ce dossier."
#         ) from exc
#     return _construire_dossier_read(db, dossier)


# def supprimer_identite(
#     db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID, identite_id: uuid.UUID
# ) -> DossierRead:
#     dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
#     identite = DossierRepository(db).obtenir_identite(dossier_id, identite_id)
#     if identite is None:
#         raise IdentiteIntrouvableError("Associé introuvable pour ce dossier.")
#     DossierRepository(db).supprimer_identite(identite)
#     return _construire_dossier_read(db, dossier)




"""Orchestration métier du cycle de vie d'un dossier persisté.

Fait le lien entre la persistance (repositories) et le système expert
stateless existant (backend.services.expert_service, non modifié -
CONCEPTION_V2.md interdit de toucher au moteur de règles). Ce service ne
contient aucune règle métier : il charge l'état, appelle le moteur existant,
persiste le résultat.

MODIFICATION (Problème 1 — redondance PieceJustificative) : les 5 booléens
autrefois portés directement par Dossier sont désormais lus/écrits via
PieceJustificative (_piece_fournie), source de vérité unique.

MODIFICATION (Problème 6 — statut hors périmètre) : evaluer_et_persister
marque le dossier HORS_PERIMETRE_AUTOMATISE plutôt que EVALUE si l'apport
(global ou par associé) est en nature.

MODIFICATION (visibilité des associés + anti-doublon) : _construire_dossier_read
expose désormais la liste des associés déjà enregistrés (DossierRead.identites),
et ajouter_identite refuse un numéro CIN déjà présent pour ce dossier.

MODIFICATION (admin lecture seule) : ajout de lister_tous_admin et
obtenir_dossier_admin — réutilisent _construire_dossier_read telle quelle.
"""

from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.exceptions import (
    DossierIntrouvableError,
    IdentiteDupliqueeError,
    IdentiteIntrouvableError,
)
from backend.models.dossier import Dossier
from backend.models.enums import StatutGlobalEnum, TypePieceEnum
from backend.repositories.dossier_repository import DossierRepository
from backend.repositories.evaluation_repository import EvaluationRepository
from backend.schemas.admin import DossierAdminRead
from backend.schemas.dossier import (
    DossierCreate,
    DossierInput,
    DossierRead,
    DossierUpdate,
    IdentitePersonneInput,
    IdentitePersonneRead,
    IdentitePersonneUpdate,
    PieceJustificativeInput,
)
from backend.schemas.evaluation import AnomalieResult, EvaluationRead, VerdictDossier
from backend.services.expert_service import evaluer_dossier

_NB_CHAMPS_PROGRESSION = 5


def _piece_fournie(dossier: Dossier, type_piece: str) -> bool:
    """Point d'accès unique pour savoir si une pièce est fournie — les
    règles du système expert et la construction de DossierRead passent
    toutes par ici plutôt que de lire un booléen dupliqué sur Dossier."""
    return any(p.type_piece == type_piece and p.fournie for p in dossier.pieces)


def _obtenir_dossier_ou_404(
    db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID
) -> Dossier:
    dossier = DossierRepository(db).obtenir(dossier_id, entrepreneur_id)
    if dossier is None:
        raise DossierIntrouvableError("Dossier introuvable.")
    return dossier


def creer_dossier(db: Session, entrepreneur_id: uuid.UUID, payload: DossierCreate) -> DossierRead:
    dossier = DossierRepository(db).creer(entrepreneur_id, payload)
    return _construire_dossier_read(db, dossier)


def lister_dossiers(db: Session, entrepreneur_id: uuid.UUID) -> list[DossierRead]:
    dossiers = DossierRepository(db).lister_pour_utilisateur(entrepreneur_id)
    return [_construire_dossier_read(db, dossier) for dossier in dossiers]


def obtenir_dossier(db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID) -> DossierRead:
    dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
    return _construire_dossier_read(db, dossier)


def mettre_a_jour_dossier(
    db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID, payload: DossierUpdate
) -> DossierRead:
    dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
    dossier = DossierRepository(db).mettre_a_jour(dossier, payload)
    return _construire_dossier_read(db, dossier)


def ajouter_identite(
    db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID, payload: IdentitePersonneInput
) -> DossierRead:
    dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
    DossierRepository(db).ajouter_identite(dossier, payload)
    return _construire_dossier_read(db, dossier)


def modifier_identite(
    db: Session,
    dossier_id: uuid.UUID,
    entrepreneur_id: uuid.UUID,
    identite_id: uuid.UUID,
    payload: IdentitePersonneUpdate,
) -> DossierRead:
    dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
    identite = DossierRepository(db).obtenir_identite(dossier_id, identite_id)
    if identite is None:
        raise IdentiteIntrouvableError("Associé introuvable pour ce dossier.")

    if payload.numero_cin and any(
        i.numero_cin == payload.numero_cin and i.id != identite_id for i in dossier.identites
    ):
        raise IdentiteDupliqueeError(
            f"Un associé avec le numéro CIN {payload.numero_cin} existe déjà pour ce dossier."
        )

    try:
        DossierRepository(db).mettre_a_jour_identite(identite, payload)
    except IntegrityError as exc:
        db.rollback()
        raise IdentiteDupliqueeError(
            f"Un associé avec le numéro CIN {payload.numero_cin} existe déjà pour ce dossier."
        ) from exc
    return _construire_dossier_read(db, dossier)


def supprimer_identite(
    db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID, identite_id: uuid.UUID
) -> DossierRead:
    dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
    identite = DossierRepository(db).obtenir_identite(dossier_id, identite_id)
    if identite is None:
        raise IdentiteIntrouvableError("Associé introuvable pour ce dossier.")
    DossierRepository(db).supprimer_identite(identite)
    return _construire_dossier_read(db, dossier)


def lister_evaluations(
    db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID
) -> list[EvaluationRead]:
    _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)
    evaluations = EvaluationRepository(db).lister_pour_dossier(dossier_id)
    return [
        EvaluationRead(
            id=str(e.id),
            date_evaluation=e.date_evaluation,
            statut_global=StatutGlobalEnum(e.statut_global),
            anomalies=[
                AnomalieResult(
                    id=str(a.id),
                    regle_id=a.regle_id,
                    categorie=a.categorie,
                    gravite=a.gravite,
                    message=a.message,
                    justification=a.justification,
                    reference_documentaire=a.reference_documentaire,
                    niveau_documentaire=a.niveau_documentaire,
                )
                for a in e.anomalies
            ],
        )
        for e in evaluations
    ]


def evaluer_et_persister(
    db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID
) -> EvaluationRead:
    dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)

    dossier_input = DossierInput(
        forme_juridique=dossier.forme_juridique,
        capital_social=float(dossier.capital_social),
        siege_social=dossier.siege_social,
        statuts_fournis=_piece_fournie(dossier, TypePieceEnum.STATUTS.value),
        attestation_blocage_bancaire_fournie=_piece_fournie(
            dossier, TypePieceEnum.ATTESTATION_BLOCAGE_BANCAIRE.value
        ),
        emploie_salaries=dossier.emploie_salaries,
        type_justificatif_siege=dossier.type_justificatif_siege,
        gerant_designe_dans_statuts=dossier.gerant_designe_dans_statuts,
        identites=[
            IdentitePersonneInput(
                nom=i.nom or "",
                prenom=i.prenom or "",
                numero_cin=i.numero_cin or "",
                date_naissance=i.date_naissance,
                type_apport_personnel=i.type_apport_personnel,
                montant_apport=float(i.montant_apport) if i.montant_apport is not None else None,
            )
            for i in dossier.identites
        ],
        pieces=[
            PieceJustificativeInput(type_piece=p.type_piece, fournie=p.fournie)
            for p in dossier.pieces
        ],
    )

    verdict: VerdictDossier = evaluer_dossier(dossier_input)

    evaluation = EvaluationRepository(db).creer(dossier.id, verdict)

    # 🔥 CORRECTION : type_apport est retiré du modèle Dossier.
    # On ne vérifie que les apports des associés.
    apport_en_nature = any(
        i.type_apport_personnel == "nature" for i in dossier.identites
    )
    if apport_en_nature:
        DossierRepository(db).marquer_hors_perimetre(dossier)
    else:
        DossierRepository(db).marquer_evalue(dossier)

    return EvaluationRead(
        id=str(evaluation.id),
        date_evaluation=evaluation.date_evaluation,
        statut_global=verdict.statut_global,
        anomalies=verdict.anomalies,
    )


def lister_tous_admin(db: Session) -> list[DossierAdminRead]:
    dossiers = DossierRepository(db).lister_tous()
    return [
        DossierAdminRead(
            dossier=_construire_dossier_read(db, dossier),
            entrepreneur_nom=dossier.entrepreneur.nom,
            entrepreneur_email=dossier.entrepreneur.email,
        )
        for dossier in dossiers
    ]


def obtenir_dossier_admin(db: Session, dossier_id: uuid.UUID) -> DossierAdminRead:
    dossier = DossierRepository(db).obtenir_par_id(dossier_id)
    if dossier is None:
        raise DossierIntrouvableError("Dossier introuvable.")
    return DossierAdminRead(
        dossier=_construire_dossier_read(db, dossier),
        entrepreneur_nom=dossier.entrepreneur.nom,
        entrepreneur_email=dossier.entrepreneur.email,
    )


def _construire_dossier_read(db: Session, dossier: Dossier) -> DossierRead:
    derniere = EvaluationRepository(db).derniere_pour_dossier(dossier.id)

    nb_bloquantes = 0
    nb_avertissements = 0
    pret_pour_depot = False
    date_derniere_evaluation = None

    if derniere is not None:
        date_derniere_evaluation = derniere.date_evaluation
        nb_bloquantes = sum(1 for a in derniere.anomalies if a.gravite == "bloquante")
        nb_avertissements = sum(
            1 for a in derniere.anomalies if a.gravite in ("avertissement", "informative")
        )
        pret_pour_depot = derniere.statut_global in (
            StatutGlobalEnum.CONFORME,
            StatutGlobalEnum.CONFORME_AVEC_RESERVES,
        )

    champs_remplis = sum(
        [
            bool(dossier.nom_projet),
            bool(dossier.forme_juridique),
            dossier.capital_social is not None and float(dossier.capital_social) > 0,
            bool(dossier.siege_social),
            len(dossier.identites) > 0,
        ]
    )

    progression_pct = round(100 * champs_remplis / _NB_CHAMPS_PROGRESSION)

    return DossierRead(
        id=str(dossier.id),
        nom_projet=dossier.nom_projet,
        forme_juridique=dossier.forme_juridique,
        capital_social=float(dossier.capital_social),
        siege_social=dossier.siege_social,
        statuts_fournis=_piece_fournie(dossier, TypePieceEnum.STATUTS.value),
        attestation_blocage_bancaire_fournie=_piece_fournie(
            dossier, TypePieceEnum.ATTESTATION_BLOCAGE_BANCAIRE.value
        ),
        emploie_salaries=dossier.emploie_salaries,
        type_justificatif_siege=dossier.type_justificatif_siege,
        gerant_designe_dans_statuts=dossier.gerant_designe_dans_statuts,
        statut=dossier.statut,
        date_creation=dossier.date_creation,
        progression_pct=progression_pct,
        nb_erreurs_bloquantes=nb_bloquantes,
        nb_avertissements=nb_avertissements,
        pret_pour_depot=pret_pour_depot,
        date_derniere_evaluation=date_derniere_evaluation,
        identites=[
            IdentitePersonneRead(
                id=str(i.id),
                nom=i.nom,
                prenom=i.prenom,
                numero_cin=i.numero_cin,
                date_naissance=i.date_naissance,
                type_apport_personnel=i.type_apport_personnel,
                montant_apport=float(i.montant_apport) if i.montant_apport is not None else None,
            )
            for i in dossier.identites
        ],
    )