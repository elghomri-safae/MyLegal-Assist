"""elargir colonne statut dossiers

Revision ID: f6beac0b9edb
Revises: c3d8f4a91e27
Create Date: 2026-08-27 10:56:35.618764
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6beac0b9edb'
down_revision: str | None = 'c3d8f4a91e27'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "dossiers",
        "statut",
        existing_type=sa.String(20),
        type_=sa.String(30),
    )


def downgrade() -> None:
    op.alter_column(
        "dossiers",
        "statut",
        existing_type=sa.String(30),
        type_=sa.String(20),
    )