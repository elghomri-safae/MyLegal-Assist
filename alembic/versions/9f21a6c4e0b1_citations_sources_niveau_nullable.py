"""citations_sources.niveau devient nullable.

Le pipeline RAG finalisé (backend/rag/generation.py) ne produit plus de
hiérarchie "niveau" pour les citations issues du corpus juridique structurel
(décision actée : aucune hiérarchie artificielle introduite depuis
type_source). CitationOutput.niveau est donc optionnel côté API depuis
plusieurs itérations, mais la colonne SQL était restée NOT NULL — chaque
insertion d'une réponse du chatbot échouait silencieusement en 500
(IntegrityError) jusqu'à cette migration.

anomalies.niveau_documentaire n'est PAS concerné par cette migration : c'est
un champ différent, toujours renseigné par le système expert (backend.rules,
non modifié) — inchangé, reste NOT NULL.

Revision ID: 9f21a6c4e0b1
Revises: 328c09bae8e8
Create Date: 2026-08-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f21a6c4e0b1"
down_revision: str | None = "328c09bae8e8"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "citations_sources",
        "niveau",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    """Attention : un downgrade échouera s'il existe déjà des lignes avec
    niveau NULL (toute réponse générée depuis le nouveau corpus). Purger ces
    lignes, ou leur assigner une valeur, avant de redescendre cette révision."""
    op.alter_column(
        "citations_sources",
        "niveau",
        existing_type=sa.Integer(),
        nullable=False,
    )
