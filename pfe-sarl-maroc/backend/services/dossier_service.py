"""Orchestration métier du cycle de vie d'un dossier persisté.

Fait le lien entre la persistance (repositories) et le système expert
stateless existant (backend.services.expert_service, non modifié -
CONCEPTION_V2.md interdit de toucher au moteur de règles). Ce service ne
contient aucune règle métier : il charge l'état, appelle le moteur existant,
persiste le résultat.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import DossierIntrouvableError
from backend.models.dossier import Dossier
from backend.models.enums import StatutGlobalEnum
from backend.repositories.dossier_repository import DossierRepository
from backend.repositories.evaluation_repository import EvaluationRepository
from backend.schemas.dossier import (
    DossierCreate,
    DossierInput,
    DossierRead,
    DossierUpdate,
    IdentitePersonneInput,
    PieceJustificativeInput,
)
from backend.schemas.evaluation import AnomalieResult, EvaluationRead, VerdictDossier
from backend.services.expert_service import evaluer_dossier

# Champs comptés pour l'indicateur de progression de saisie (CONCEPTION_V2.md
# §9.3) : uniquement ceux ayant un état "non renseigné" distinguable d'une
# vraie réponse (voir schemas/dossier.py::DossierRead pour la justification
# de l'exclusion des champs booléens "fourni"/"déclarée").
_NB_CHAMPS_PROGRESSION = 6


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


def lister_evaluations(
    db: Session, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID
) -> list[EvaluationRead]:
    """Historique des évaluations d'un dossier (CONCEPTION_V2.md §9.4)."""
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
    """Charge l'état courant du dossier, appelle le système expert (inchangé),
    persiste le verdict et met à jour le statut du dossier (CONCEPTION_V2.md §5).
    """
    dossier = _obtenir_dossier_ou_404(db, dossier_id, entrepreneur_id)

    dossier_input = DossierInput(
        forme_juridique=dossier.forme_juridique,
        capital_social=float(dossier.capital_social),
        siege_social=dossier.siege_social,
        statuts_fournis=dossier.statuts_fournis,
        certificat_negatif_fourni=dossier.certificat_negatif_fourni,
        certificat_negatif_date_delivrance=dossier.certificat_negatif_date_delivrance,
        attestation_blocage_bancaire_fournie=dossier.attestation_blocage_bancaire_fournie,
        taxe_professionnelle_declaree=dossier.taxe_professionnelle_declaree,
        emploie_salaries=dossier.emploie_salaries,
        affiliation_cnss_fournie=dossier.affiliation_cnss_fournie,
        identites=[
            IdentitePersonneInput(
                nom=i.nom or "",
                prenom=i.prenom or "",
                numero_cin=i.numero_cin or "",
                date_naissance=i.date_naissance,
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
    DossierRepository(db).marquer_evalue(dossier)

    return EvaluationRead(
        id=str(evaluation.id),
        date_evaluation=evaluation.date_evaluation,
        statut_global=verdict.statut_global,
        anomalies=verdict.anomalies,
    )


def _construire_dossier_read(db: Session, dossier: Dossier) -> DossierRead:
    """Calcule les indicateurs de tableau de bord à partir de la dernière
    évaluation (CONCEPTION_V2.md §9.1, §9.2, §9.3) sans jamais les stocker.
    """
    derniere = EvaluationRepository(db).derniere_pour_dossier(dossier.id)

    nb_bloquantes = 0
    nb_avertissements = 0
    pret_pour_depot = False
    date_derniere_evaluation = None

    if derniere is not None:
        date_derniere_evaluation = derniere.date_evaluation
        nb_bloquantes = sum(1 for a in derniere.anomalies if a.gravite == "bloquante")
        # Fusion avertissement + informative à l'affichage uniquement (§9.2) ;
        # le modèle garde les 3 valeurs réelles sur chaque Anomalie.
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
            dossier.certificat_negatif_date_delivrance is not None,
        ]
    )
    progression_pct = round(100 * champs_remplis / _NB_CHAMPS_PROGRESSION)

    return DossierRead(
        id=str(dossier.id),
        nom_projet=dossier.nom_projet,
        forme_juridique=dossier.forme_juridique,
        capital_social=float(dossier.capital_social),
        siege_social=dossier.siege_social,
        statuts_fournis=dossier.statuts_fournis,
        certificat_negatif_fourni=dossier.certificat_negatif_fourni,
        certificat_negatif_date_delivrance=dossier.certificat_negatif_date_delivrance,
        attestation_blocage_bancaire_fournie=dossier.attestation_blocage_bancaire_fournie,
        taxe_professionnelle_declaree=dossier.taxe_professionnelle_declaree,
        emploie_salaries=dossier.emploie_salaries,
        affiliation_cnss_fournie=dossier.affiliation_cnss_fournie,
        statut=dossier.statut,
        date_creation=dossier.date_creation,
        progression_pct=progression_pct,
        nb_erreurs_bloquantes=nb_bloquantes,
        nb_avertissements=nb_avertissements,
        pret_pour_depot=pret_pour_depot,
        date_derniere_evaluation=date_derniere_evaluation,
    )
