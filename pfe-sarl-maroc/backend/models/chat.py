"""ORM models for the legal chatbot conversation history.

``Question.dossier_id`` (nullable) distingue une question generale (NULL)
d'une question contextuelle a un dossier precis (CONCEPTION_V2.md §6.5,
acte comme consequence directe de la hierarchie chatbot/systeme expert/RAG
du §6 : sans ce champ, le chatbot ne peut pas savoir si le contexte d'un
dossier doit etre charge avant de repondre).
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.dossier import Dossier
    from backend.models.utilisateur import Utilisateur


class Question(Base):
    """Question juridique posee par un utilisateur au chatbot.

    ``dossier_id`` est NULL pour une question generale, renseigne pour une
    question contextuelle a un dossier precis (CONCEPTION_V2.md §6.2).
    """

    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False
    )
    dossier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=True
    )
    texte: Mapped[str] = mapped_column(String(2000), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="questions")
    dossier: Mapped["Dossier | None"] = relationship()
    reponse: Mapped["Reponse"] = relationship(
        back_populates="question", uselist=False, cascade="all, delete-orphan"
    )


class Reponse(Base):
    """Reponse generee par le pipeline RAG pour une question donnee."""

    __tablename__ = "reponses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, unique=True
    )
    texte: Mapped[str] = mapped_column(String(4000), nullable=False)

    question: Mapped["Question"] = relationship(back_populates="reponse")
    citations: Mapped[list["CitationSource"]] = relationship(
        back_populates="reponse", cascade="all, delete-orphan"
    )


class CitationSource(Base):
    """Citation (source, niveau, reference) associee a une reponse du chatbot."""

    __tablename__ = "citations_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reponse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reponses.id"), nullable=False
    )
    document: Mapped[str] = mapped_column(String(255), nullable=False)
    niveau: Mapped[int] = mapped_column(Integer, nullable=False)
    reference: Mapped[str] = mapped_column(String(255), nullable=False)

    reponse: Mapped["Reponse"] = relationship(back_populates="citations")
