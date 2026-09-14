"""Ajout des positions métier MyLegal sur dossiers : type_justificatif_siege,
gerant_designe_dans_statuts, type_apport.

Ces trois champs implémentent les décisions métier MyLegal (référentiel
documentaire création SARL/SARL AU) sur :
- le type de justificatif de siège accepté (bail / domiciliation MyLegal /
  domiciliation tiers / propriété) ;
- si le gérant est déjà désigné dans les statuts (conditionne l'exigence du
  PV de nomination) ;
- la nature de l'apport au capital (numéraire / nature — un apport en
  nature exclut le dossier du traitement automatisé v1).

Revision ID: c3d8f4a91e27
Revises: 9f21a6c4e0b1
Create Date: 2026-08-14
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d8f4a91e27"
down_revision: str | None = "9f21a6c4e0b1"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "dossiers",
        sa.Column(
            "type_justificatif_siege",
            sa.String(30),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "dossiers",
        sa.Column(
            "gerant_designe_dans_statuts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "dossiers",
        sa.Column(
            "type_apport",
            sa.String(20),
            nullable=False,
            server_default="numeraire",
        ),
    )


def downgrade() -> None:
    op.drop_column("dossiers", "type_apport")
    op.drop_column("dossiers", "gerant_designe_dans_statuts")
    op.drop_column("dossiers", "type_justificatif_siege")
