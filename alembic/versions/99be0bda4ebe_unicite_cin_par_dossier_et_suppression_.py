"""unicite cin par dossier et suppression certificat negatif date

Revision ID: 99be0bda4ebe
Revises: 4a2a46ad507e
Create Date: 2026-08-29 11:22:40.919540
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '99be0bda4ebe'
down_revision: str | None = '4a2a46ad507e'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:

   # 1. Contrainte d'unicité (déjà là)
    op.create_unique_constraint(
        "uq_identite_dossier_cin", "identites_personnes", ["dossier_id", "numero_cin"]
    )
    
    # 2. Suppression de la colonne (déjà là)
    op.drop_column("dossiers", "certificat_negatif_date_delivrance")
    
    # 3. AJOUT : Suppression des tables mortes
    op.drop_table("chunks")
    op.drop_table("documents_corpus")

def downgrade() -> None:
    # 1. AJOUT : Recréer les tables mortes (ordre inverse des suppressions)
    op.create_table(
        "documents_corpus",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("titre", sa.String(255), nullable=False),
        sa.Column("niveau", sa.Integer(), nullable=False),
        sa.Column("type_source", sa.String(100), nullable=False),
    )
    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents_corpus.id"), nullable=False),
        sa.Column("texte", sa.Text(), nullable=False),
        sa.Column("embedding_ref", sa.String(255), nullable=False),
    )
    
    # 2. Recréer la colonne supprimée (déjà là)
    op.add_column("dossiers", sa.Column("certificat_negatif_date_delivrance", sa.Date(), nullable=True))
    
    # 3. Supprimer la contrainte (déjà là)
    op.drop_constraint("uq_identite_dossier_cin", "identites_personnes", type_="unique")