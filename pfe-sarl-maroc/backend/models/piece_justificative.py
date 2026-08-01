"""ORM model for a supporting document attached to a dossier."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.dossier import Dossier


class PieceJustificative(Base):
    """Piece justificative attendue ou fournie pour un dossier de creation."""

    __tablename__ = "pieces_justificatives"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    type_piece: Mapped[str] = mapped_column(String(100), nullable=False)
    reference_fichier: Mapped[str] = mapped_column(String(500), nullable=True)
    fournie: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    dossier: Mapped["Dossier"] = relationship(back_populates="pieces")
