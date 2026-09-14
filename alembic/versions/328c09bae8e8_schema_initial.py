"""Schema initial V2 — cree l'integralite des tables du modele de donnees
CONCEPTION_V2.md (§4). Regenere a l'occasion de la refonte V2 : aucun
deploiement reel n'a jamais existe sur le schema V1 (confirme par l'audit du
projet), la migration est donc directement alignee sur le modele cible plutot
que patchee incrementalement. mot_de_passe_hash (auparavant une migration
separee, Phase 6 V1) est desormais inclus directement dans la table initiale.

Revision ID: 328c09bae8e8
Revises:
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "328c09bae8e8"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Cree toutes les tables du schema V2, dans l'ordre des dependances FK."""
    op.create_table(
        "utilisateurs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nom", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("mot_de_passe_hash", sa.String(255), nullable=False),
    )

    op.create_table(
        "documents_corpus",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("titre", sa.String(255), nullable=False),
        sa.Column("niveau", sa.Integer(), nullable=False),
        sa.Column("type_source", sa.String(100), nullable=False),
    )

    op.create_table(
        "dossiers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "entrepreneur_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("utilisateurs.id"),
            nullable=False,
        ),
        sa.Column("nom_projet", sa.String(255), nullable=False),
        sa.Column("forme_juridique", sa.String(50), nullable=False),
        sa.Column("capital_social", sa.Numeric(14, 2), nullable=False),
        sa.Column("siege_social", sa.String(500), nullable=False, server_default=""),
        sa.Column("statuts_fournis", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "certificat_negatif_fourni", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("certificat_negatif_date_delivrance", sa.Date(), nullable=True),
        sa.Column(
            "attestation_blocage_bancaire_fournie",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "taxe_professionnelle_declaree", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("emploie_salaries", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "affiliation_cnss_fournie", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("statut", sa.String(20), nullable=False, server_default="brouillon"),
    )

    op.create_table(
        "identites_personnes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dossier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id"),
            nullable=False,
        ),
        # Nullable : remplissage progressif (CONCEPTION_V2.md §2).
        sa.Column("nom", sa.String(255), nullable=True),
        sa.Column("prenom", sa.String(255), nullable=True),
        sa.Column("numero_cin", sa.String(20), nullable=True),
        sa.Column("date_naissance", sa.Date(), nullable=True),
    )

    op.create_table(
        "pieces_justificatives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dossier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id"),
            nullable=False,
        ),
        sa.Column("type_piece", sa.String(100), nullable=False),
        sa.Column("reference_fichier", sa.String(500), nullable=True),
        sa.Column("fournie", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dossier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id"),
            nullable=False,
        ),
        sa.Column(
            "date_evaluation",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("statut_global", sa.String(30), nullable=False),
    )

    op.create_table(
        "anomalies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "evaluation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("evaluations.id"),
            nullable=False,
        ),
        # regle_id n'est plus une cle etrangere (la table "regles" n'existe
        # plus : les regles vivent en Python, backend/rules/*.py, seule
        # source de verite - CONCEPTION_V2.md §6.4).
        sa.Column("regle_id", sa.String(50), nullable=False),
        sa.Column("categorie", sa.String(50), nullable=False),
        sa.Column("message", sa.String(1000), nullable=False),
        sa.Column("gravite", sa.String(20), nullable=False),
        sa.Column("justification", sa.String(2000), nullable=False),
        sa.Column("reference_documentaire", sa.String(255), nullable=False),
        sa.Column("niveau_documentaire", sa.Integer(), nullable=False),
    )

    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "utilisateur_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("utilisateurs.id"),
            nullable=False,
        ),
        # Nullable : NULL = question generale, renseigne = question
        # contextuelle a un dossier precis (CONCEPTION_V2.md §6.5).
        sa.Column(
            "dossier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id"),
            nullable=True,
        ),
        sa.Column("texte", sa.String(2000), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "reponses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("questions.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("texte", sa.String(4000), nullable=False),
    )

    op.create_table(
        "citations_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "reponse_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reponses.id"),
            nullable=False,
        ),
        sa.Column("document", sa.String(255), nullable=False),
        sa.Column("niveau", sa.Integer(), nullable=False),
        sa.Column("reference", sa.String(255), nullable=False),
    )

    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents_corpus.id"),
            nullable=False,
        ),
        sa.Column("texte", sa.Text(), nullable=False),
        sa.Column("embedding_ref", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    """Supprime toutes les tables, dans l'ordre inverse des dependances FK."""
    op.drop_table("chunks")
    op.drop_table("citations_sources")
    op.drop_table("reponses")
    op.drop_table("questions")
    op.drop_table("anomalies")
    op.drop_table("evaluations")
    op.drop_table("pieces_justificatives")
    op.drop_table("identites_personnes")
    op.drop_table("dossiers")
    op.drop_table("documents_corpus")
    op.drop_table("utilisateurs")
