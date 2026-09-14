"""ORM model for a SARL/SARL AU creation dossier.

Depuis CONCEPTION_V2.md (§4.2, §4.3), ce modele fusionne l'ancienne entite
``Entreprise`` (jamais implementee en V1, uniquement envisagee puis abandonnee
au fil de la conception) : ``nom_projet`` porte l'identite du projet choisie
par l'utilisateur, le reste des champs porte les donnees evaluees par le
systeme expert. Ces champs metier reprennent exactement ceux de
``backend.schemas.dossier.DossierInput`` (ecart avec la V1 comble ici : le
modele ORM V1 ne portait que 3 des 10 champs necessaires a une evaluation
reelle, faute d'avoir jamais ete persiste).
"""

import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base
from backend.models.enums import StatutDossierEnum

if TYPE_CHECKING:
    from backend.models.evaluation import Evaluation
    from backend.models.identite_personne import IdentitePersonne
    from backend.models.piece_justificative import PieceJustificative
    from backend.models.utilisateur import Utilisateur


class Dossier(Base):
    """Dossier de creation soumis par un entrepreneur (BF-03, docs/UML.md).

    Fusionne Entreprise + Dossier (CONCEPTION_V2.md §4.2) : une seule entite,
    identifiee par ``nom_projet`` cote utilisateur, portant aussi les donnees
    techniques evaluees par le systeme expert.
    """

    __tablename__ = "dossiers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entrepreneur_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False
    )

    # Identite du projet (ex-Entreprise, CONCEPTION_V2.md §4.2).
    nom_projet: Mapped[str] = mapped_column(String(255), nullable=False)

    # Champs metier evalues par le systeme expert (rules/*.py) — alignes sur
    # backend.schemas.dossier.DossierInput (CONCEPTION_V2.md §4.3).
    forme_juridique: Mapped[str] = mapped_column(String(50), nullable=False)
    capital_social: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    siege_social: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    statuts_fournis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    certificat_negatif_fourni: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    certificat_negatif_date_delivrance: Mapped[date | None] = mapped_column(Date, nullable=True)

    attestation_blocage_bancaire_fournie: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    taxe_professionnelle_declaree: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    emploie_salaries: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    affiliation_cnss_fournie: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    statut: Mapped[StatutDossierEnum] = mapped_column(
        String(20), nullable=False, default=StatutDossierEnum.BROUILLON
    )

    entrepreneur: Mapped["Utilisateur"] = relationship(back_populates="dossiers")
    identites: Mapped[list["IdentitePersonne"]] = relationship(
        back_populates="dossier", cascade="all, delete-orphan"
    )
    pieces: Mapped[list["PieceJustificative"]] = relationship(
        back_populates="dossier", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="dossier", cascade="all, delete-orphan"
    )
