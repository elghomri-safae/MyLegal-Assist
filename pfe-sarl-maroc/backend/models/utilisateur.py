"""ORM model for an application actor (entrepreneur ou admin)."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base
from backend.models.enums import RoleEnum

if TYPE_CHECKING:
    from backend.models.chat import Question
    from backend.models.dossier import Dossier


class Utilisateur(Base):
    """Represente un des deux acteurs valides (entrepreneur, admin — CONCEPTION_V2.md §3)."""

    __tablename__ = "utilisateurs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[RoleEnum] = mapped_column(String(20), nullable=False)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    dossiers: Mapped[list["Dossier"]] = relationship(back_populates="entrepreneur")
    questions: Mapped[list["Question"]] = relationship(back_populates="utilisateur")
