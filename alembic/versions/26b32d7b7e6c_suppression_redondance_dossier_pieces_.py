"""suppression redondance dossier pieces justificatives

Revision ID: 26b32d7b7e6c
Revises: f6beac0b9edb
Create Date: 2026-08-27 11:05:20.427559
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26b32d7b7e6c'
down_revision: str | None = 'f6beac0b9edb'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


import uuid as uuid_module

def upgrade() -> None:
    conn = op.get_bind()

    dossiers = conn.execute(sa.text(
        "SELECT id, statuts_fournis, certificat_negatif_fourni, "
        "attestation_blocage_bancaire_fournie, taxe_professionnelle_declaree, "
        "affiliation_cnss_fournie FROM dossiers"
    )).fetchall()

    mapping = {
        "statuts_fournis": "statuts",
        "certificat_negatif_fourni": "certificat_negatif",
        "attestation_blocage_bancaire_fournie": "attestation_blocage_bancaire",
        "taxe_professionnelle_declaree": "taxe_professionnelle",
        "affiliation_cnss_fournie": "affiliation_cnss",
    }

    for row in dossiers:
        dossier_id = row[0]
        valeurs = dict(zip(mapping.keys(), row[1:], strict=True))
        for champ_legacy, type_piece in mapping.items():
            existe = conn.execute(
                sa.text("SELECT 1 FROM pieces_justificatives WHERE dossier_id = :did AND type_piece = :tp"),
                {"did": dossier_id, "tp": type_piece},
            ).fetchone()
            if existe is None:
                conn.execute(
                    sa.text(
                        "INSERT INTO pieces_justificatives (id, dossier_id, type_piece, fournie) "
                        "VALUES (:id, :did, :tp, :fournie)"
                    ),
                    {"id": str(uuid_module.uuid4()), "did": dossier_id, "tp": type_piece, "fournie": valeurs[champ_legacy]},
                )
            else:
                conn.execute(
                    sa.text("UPDATE pieces_justificatives SET fournie = :fournie WHERE dossier_id = :did AND type_piece = :tp"),
                    {"did": dossier_id, "tp": type_piece, "fournie": valeurs[champ_legacy]},
                )

    op.drop_column("pieces_justificatives", "reference_fichier")
    op.create_unique_constraint("uq_piece_dossier_type", "pieces_justificatives", ["dossier_id", "type_piece"])

    op.drop_column("dossiers", "statuts_fournis")
    op.drop_column("dossiers", "certificat_negatif_fourni")
    op.drop_column("dossiers", "attestation_blocage_bancaire_fournie")
    op.drop_column("dossiers", "taxe_professionnelle_declaree")
    op.drop_column("dossiers", "affiliation_cnss_fournie")


def downgrade() -> None:
    op.add_column("dossiers", sa.Column("affiliation_cnss_fournie", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("dossiers", sa.Column("taxe_professionnelle_declaree", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("dossiers", sa.Column("attestation_blocage_bancaire_fournie", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("dossiers", sa.Column("certificat_negatif_fourni", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("dossiers", sa.Column("statuts_fournis", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.drop_constraint("uq_piece_dossier_type", "pieces_justificatives", type_="unique")
    op.add_column("pieces_justificatives", sa.Column("reference_fichier", sa.String(500), nullable=True))