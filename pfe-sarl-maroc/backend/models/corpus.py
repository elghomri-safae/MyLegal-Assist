"""ORM models describing the closed documentary corpus used by the RAG module.

Rappel (Regle absolue n1 et n2 du prompt) : le corpus est ferme aux six
documents fournis (S1 a S6, voir PROJECT.md). Ces modeles ne font que
persister leurs metadonnees et decoupages ; ils ne permettent pas d'ajouter
une source hors corpus sans intervention explicite.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    pass


class DocumentCorpus(Base):
    """Un document du corpus documentaire ferme (S1 a S6)."""

    __tablename__ = "documents_corpus"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titre: Mapped[str] = mapped_column(String(255), nullable=False)
    niveau: Mapped[int] = mapped_column(Integer, nullable=False)
    type_source: Mapped[str] = mapped_column(String(100), nullable=False)

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class Chunk(Base):
    """Un decoupage textuel d'un document, indexe dans ChromaDB via embedding_ref."""

    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents_corpus.id"), nullable=False
    )
    texte: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_ref: Mapped[str] = mapped_column(String(255), nullable=False)

    document: Mapped["DocumentCorpus"] = relationship(back_populates="chunks")
