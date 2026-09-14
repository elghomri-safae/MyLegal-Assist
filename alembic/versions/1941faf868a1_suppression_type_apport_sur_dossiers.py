"""suppression type_apport sur dossiers

Revision ID: 1941faf868a1
Revises: 99be0bda4ebe
Create Date: 2026-08-31 13:03:48.346737
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1941faf868a1'
down_revision: str | None = '99be0bda4ebe'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.drop_column("dossiers", "type_apport")


def downgrade() -> None:
    op.add_column(
        "dossiers",
        sa.Column("type_apport", sa.String(20), nullable=False, server_default="numeraire"),
    )