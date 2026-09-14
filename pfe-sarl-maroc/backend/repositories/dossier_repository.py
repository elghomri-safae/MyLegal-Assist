"""Accès aux données pour l'entité Dossier persistée (CONCEPTION_V2.md §4.2, §4.3)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.dossier import Dossier
from backend.models.enums import StatutDossierEnum
from backend.models.identite_personne import IdentitePersonne
from backend.schemas.dossier import DossierCreate, DossierUpdate, IdentitePersonneInput


class DossierRepository:
    """Repository SQLAlchemy pour les dossiers d'un entrepreneur."""

    def __init__(self, db: Session) -> None:
        self._db = db

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

    def obtenir(self, dossier_id: uuid.UUID, entrepreneur_id: uuid.UUID) -> Dossier | None:
        """Récupère un dossier, borné au propriétaire (jamais celui d'un autre)."""
        stmt = select(Dossier).where(
            Dossier.id == dossier_id, Dossier.entrepreneur_id == entrepreneur_id
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def lister_pour_utilisateur(self, entrepreneur_id: uuid.UUID) -> list[Dossier]:
        stmt = (
            select(Dossier)
            .where(Dossier.entrepreneur_id == entrepreneur_id)
            .order_by(Dossier.date_creation.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def mettre_a_jour(self, dossier: Dossier, payload: DossierUpdate) -> Dossier:
        donnees = payload.model_dump(exclude_unset=True)
        for champ, valeur in donnees.items():
            setattr(dossier, champ, valeur)
        self._db.commit()
        self._db.refresh(dossier)
        return dossier

    def marquer_evalue(self, dossier: Dossier) -> Dossier:
        dossier.statut = StatutDossierEnum.EVALUE
        self._db.commit()
        self._db.refresh(dossier)
        return dossier

    def ajouter_identite(
        self, dossier: Dossier, payload: IdentitePersonneInput
    ) -> IdentitePersonne:
        identite = IdentitePersonne(
            dossier_id=dossier.id,
            nom=payload.nom,
            prenom=payload.prenom,
            numero_cin=payload.numero_cin,
            date_naissance=payload.date_naissance,
        )
        self._db.add(identite)
        self._db.commit()
        self._db.refresh(identite)
        return identite
