"""Accès aux données pour l'entité Dossier persistée (CONCEPTION_V2.md §4.2, §4.3).

MODIFICATION (admin lecture seule) : ajout de ``lister_tous`` et
``obtenir_par_id`` — SANS filtre ``entrepreneur_id``, à la différence de
``lister_pour_utilisateur``/``obtenir`` (qui restent inchangées, c'est la
barrière de sécurité multi-tenant pour un entrepreneur : on n'y touche pas).
Ces deux nouvelles méthodes ne doivent être appelées QUE depuis un chemin
protégé par ``exiger_role("admin")`` — elles n'ont elles-mêmes aucune notion
de rôle, cette responsabilité est portée par l'appelant (le routeur).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.dossier import Dossier
from backend.models.enums import StatutDossierEnum, TypePieceEnum
from backend.models.identite_personne import IdentitePersonne
from backend.models.piece_justificative import PieceJustificative
from backend.schemas.dossier import DossierCreate, DossierUpdate, IdentitePersonneInput


from backend.schemas.dossier import (
    DossierCreate,
    DossierUpdate,
    IdentitePersonneInput,
    IdentitePersonneUpdate,
)
# =============================================================================
# EXCEPTIONS PERSONNALISÉES
# =============================================================================

class IdentiteDupliqueeError(Exception):
    """Levée lorsqu'on tente d'ajouter un associé avec un CIN déjà existant
    dans le même dossier."""
    pass


# =============================================================================
# MAPPING LEGACY (Problème 1 : migration des anciens booléens du Dossier vers PieceJustificative)
# =============================================================================

_CHAMPS_LEGACY_VERS_PIECE: dict[str, str] = {
    "statuts_fournis": TypePieceEnum.STATUTS.value,
    # "certificat_negatif_fourni": TypePieceEnum.CERTIFICAT_NEGATIF.value,  # Commente : géré par MyLegal (informative)
    "attestation_blocage_bancaire_fournie": TypePieceEnum.ATTESTATION_BLOCAGE_BANCAIRE.value,
    # "taxe_professionnelle_declaree": TypePieceEnum.TAXE_PROFESSIONNELLE.value,  # Commente : géré par MyLegal
    # "affiliation_cnss_fournie": TypePieceEnum.AFFILIATION_CNSS.value,  # Commente : géré par MyLegal
}


# =============================================================================
# REPOSITORY PRINCIPAL
# =============================================================================

class DossierRepository:
    """Repository SQLAlchemy pour les dossiers d'un entrepreneur."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # --- Méthodes d'écriture (CRUD) ---

    def creer(self, entrepreneur_id: uuid.UUID, payload: DossierCreate) -> Dossier:
        dossier = Dossier(
            entrepreneur_id=entrepreneur_id,
            nom_projet=payload.nom_projet,
            forme_juridique=payload.forme_juridique,
            capital_social=payload.capital_social,
            siege_social=payload.siege_social,
            statut=StatutDossierEnum.BROUILLON,
        )
        self._db.add(dossier)
        self._db.commit()
        self._db.refresh(dossier)
        return dossier

    def mettre_a_jour(self, dossier: Dossier, payload: DossierUpdate) -> Dossier:
        """Met à jour un dossier en traduisant les champs booléens historiques
        (statuts_fournis, etc.) en lignes PieceJustificative."""
        donnees = payload.model_dump(exclude_unset=True)

        for champ, valeur in donnees.items():
            if champ in _CHAMPS_LEGACY_VERS_PIECE:
                self._upsert_piece(dossier, _CHAMPS_LEGACY_VERS_PIECE[champ], valeur)
            else:
                setattr(dossier, champ, valeur)

        self._db.commit()
        self._db.refresh(dossier)
        return dossier

    def _upsert_piece(self, dossier: Dossier, type_piece: str, fournie: bool) -> None:
        """Insère ou met à jour une ligne dans PieceJustificative."""
        piece = next((p for p in dossier.pieces if p.type_piece == type_piece), None)
        if piece is None:
            piece = PieceJustificative(
                dossier_id=dossier.id,
                type_piece=type_piece,
                fournie=fournie
            )
            self._db.add(piece)
            dossier.pieces.append(piece)  # Met à jour la relation en mémoire
        else:
            piece.fournie = fournie

    def marquer_evalue(self, dossier: Dossier) -> Dossier:
        dossier.statut = StatutDossierEnum.EVALUE
        self._db.commit()
        self._db.refresh(dossier)
        return dossier

    def marquer_hors_perimetre(self, dossier: Dossier) -> Dossier:
        """Problème 6 : dossier avec apport en nature redirigé vers un juriste."""
        dossier.statut = StatutDossierEnum.HORS_PERIMETRE_AUTOMATISE
        self._db.commit()
        self._db.refresh(dossier)
        return dossier

    def ajouter_identite(self, dossier: Dossier, payload: IdentitePersonneInput) -> IdentitePersonne:
        """Ajoute un associé au dossier. Vérifie l'unicité du CIN dans le dossier."""
        identite = IdentitePersonne(
            dossier_id=dossier.id,
            nom=payload.nom,
            prenom=payload.prenom,
            numero_cin=payload.numero_cin,
            date_naissance=payload.date_naissance,
            type_apport_personnel=payload.type_apport_personnel,
            montant_apport=payload.montant_apport,
        )
        self._db.add(identite)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise IdentiteDupliqueeError(
                f"Un associé avec le numéro CIN {payload.numero_cin} existe déjà pour ce dossier."
            ) from exc
        self._db.refresh(identite)
        return identite

    # --- Méthodes de lecture (Multi-tenant / Admin) ---

    def obtenir(self, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID) -> Dossier | None:
        """Récupère un dossier, borné au propriétaire (jamais celui d'un autre)."""
        stmt = select(Dossier).where(
            Dossier.id == dossier_id,
            Dossier.entrepreneur_id == entrepreneur_id
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def lister_pour_utilisateur(self, entrepreneur_id: uuid.UUID) -> list[Dossier]:
        """Liste tous les dossiers d'un entrepreneur donné."""
        stmt = (
            select(Dossier)
            .where(Dossier.entrepreneur_id == entrepreneur_id)
            .order_by(Dossier.date_creation.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def obtenir_par_id(self, dossier_id: uuid.UUID) -> Dossier | None:
        """Récupère un dossier par son id, SANS restriction de propriétaire.
        Admin uniquement — l'appelant (routeur) doit garantir
        ``exiger_role("admin")`` avant d'appeler cette méthode.
        """
        stmt = select(Dossier).where(Dossier.id == dossier_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def lister_tous(self) -> list[Dossier]:
        """Liste tous les dossiers, tous entrepreneurs confondus.
        Admin uniquement — l'appelant (routeur) doit garantir
        ``exiger_role("admin")`` avant d'appeler cette méthode.
        """
        stmt = select(Dossier).order_by(Dossier.date_creation.desc())
        return list(self._db.execute(stmt).scalars().all())
    
    def obtenir_identite(
        self, dossier_id: uuid.UUID, identite_id: uuid.UUID
    ) -> IdentitePersonne | None:
        stmt = select(IdentitePersonne).where(
            IdentitePersonne.id == identite_id, IdentitePersonne.dossier_id == dossier_id
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def mettre_a_jour_identite(
        self, identite: IdentitePersonne, payload: "IdentitePersonneUpdate"
    ) -> IdentitePersonne:
        donnees = payload.model_dump(exclude_unset=True)
        for champ, valeur in donnees.items():
            setattr(identite, champ, valeur)
        self._db.commit()
        self._db.refresh(identite)
        return identite

    def supprimer_identite(self, identite: IdentitePersonne) -> None:
        self._db.delete(identite)
        self._db.commit()