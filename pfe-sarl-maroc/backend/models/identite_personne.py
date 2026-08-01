"""ORM model for the identity of an associate linked to a dossier.

La cardinalite Dossier -> IdentitePersonne est 1..* : une SARL AU compte un
seul associe, une SARL de 1 a 50 (Loi 5-96, art. 44 et 47 [S1, Niveau 1]).
"""

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.dossier import Dossier


class IdentitePersonne(Base):
    """Identite d'un associe, saisie manuellement."""

    __tablename__ = "identites_personnes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id"), nullable=False
    )
    # Nullable : une identité peut être créée puis complétée progressivement
    # (CONCEPTION_V2.md §2), cohérent avec IdentitePersonneInput dont tous
    # les champs sont optionnels.
    nom: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prenom: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero_cin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_naissance: Mapped[date | None] = mapped_column(Date, nullable=True)

    dossier: Mapped["Dossier"] = relationship(back_populates="identites")
