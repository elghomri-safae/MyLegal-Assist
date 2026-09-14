"""ORM model for a supporting document attached to a dossier."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.dossier import Dossier


class PieceJustificative(Base):
    """Piece justificative attendue ou fournie pour un dossier de creation.

    ``type_piece`` reprend les valeurs de ``TypePieceEnum`` (Problème 1) :
    seule source de vérité sur l'état des pièces, remplace les booléens
    autrefois dupliqués sur ``Dossier``.
    """

    __tablename__ = "pieces_justificatives"
    __table_args__ = (
        UniqueConstraint("dossier_id", "type_piece", name="uq_piece_dossier_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    type_piece: Mapped[str] = mapped_column(String(100), nullable=False)
    fournie: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    dossier: Mapped["Dossier"] = relationship(back_populates="pieces")