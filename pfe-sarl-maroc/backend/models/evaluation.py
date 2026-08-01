"""ORM models for a dossier evaluation and its anomalies.

Renommage ``EvaluationDossier`` -> ``Evaluation`` (CONCEPTION_V2.md §4.3),
sans ``snapshot_dossier`` : le detail d'une anomalie (regle, gravite,
message, justification, reference documentaire) suffit a comprendre a
posteriori le verdict, sans reconstituer un instantane complet des champs du
dossier.
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base
from backend.models.enums import StatutGlobalEnum

if TYPE_CHECKING:
    from backend.models.dossier import Dossier


class Evaluation(Base):
    """Une execution du systeme expert sur un dossier donne (historique inclus)."""

    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    # Défaut cote application (pas server_default=func.now()) : sous SQLite,
    # CURRENT_TIMESTAMP n'a qu'une resolution a la seconde, ce qui rend deux
    # evaluations rapprochees indistinguables pour le tri "derniere evaluation"
    # (bug reel observe en verification de bout en bout). datetime.now() cote
    # Python a une resolution microseconde, fiable quel que soit le SGBD.
    date_evaluation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    statut_global: Mapped[StatutGlobalEnum] = mapped_column(String(30), nullable=False)

    dossier: Mapped["Dossier"] = relationship(back_populates="evaluations")
    anomalies: Mapped[list["Anomalie"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )


class Anomalie(Base):
    """Anomalie detectee par une regle du systeme expert pour une evaluation donnee."""

    __tablename__ = "anomalies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("evaluations.id"), nullable=False
    )
    regle_id: Mapped[str] = mapped_column(String(50), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    gravite: Mapped[str] = mapped_column(String(20), nullable=False)
    justification: Mapped[str] = mapped_column(String(2000), nullable=False)
    reference_documentaire: Mapped[str] = mapped_column(String(255), nullable=False)
    niveau_documentaire: Mapped[int] = mapped_column(Integer, nullable=False)

    evaluation: Mapped["Evaluation"] = relationship(back_populates="anomalies")
