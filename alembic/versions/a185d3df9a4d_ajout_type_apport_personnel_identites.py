"""ajout type apport personnel identites

Revision ID: a185d3df9a4d
Revises: 26b32d7b7e6c
Create Date: 2026-08-27 11:36:56.083068
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a185d3df9a4d'
down_revision: str | None = '26b32d7b7e6c'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.add_column(
        "identites_personnes",
        sa.Column("type_apport_personnel", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "identites_personnes",
        sa.Column("montant_apport", sa.Numeric(14, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("identites_personnes", "montant_apport")
    op.drop_column("identites_personnes", "type_apport_personnel")