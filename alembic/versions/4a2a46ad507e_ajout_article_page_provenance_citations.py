"""ajout article page provenance citations

Revision ID: 4a2a46ad507e
Revises: a185d3df9a4d
Create Date: 2026-08-27 11:37:09.011356
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a2a46ad507e'
down_revision: str | None = 'a185d3df9a4d'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.add_column("citations_sources", sa.Column("article", sa.String(length=50), nullable=True))
    op.add_column("citations_sources", sa.Column("page", sa.Integer(), nullable=True))
    op.add_column(
        "citations_sources",
        sa.Column(
            "provenance",
            sa.String(length=255),
            nullable=False,
            server_default="Source non renseignée",
        ),
    )


def downgrade() -> None:
    op.drop_column("citations_sources", "provenance")
    op.drop_column("citations_sources", "page")
    op.drop_column("citations_sources", "article")