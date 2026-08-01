"""Verifie que toutes les entites du modele de donnees (CONCEPTION_V2.md §4)
sont correctement enregistrees dans les metadonnees SQLAlchemy.
"""

from backend.models import Base


def test_all_expected_tables_are_registered() -> None:
    """Chaque entite du modele de donnees V2 doit avoir une table correspondante."""
    expected_tables = {
        "utilisateurs",
        "dossiers",
        "identites_personnes",
        "pieces_justificatives",
        "evaluations",
        "anomalies",
        "questions",
        "reponses",
        "citations_sources",
        "documents_corpus",
        "chunks",
    }

    registered_tables = set(Base.metadata.tables.keys())

    assert expected_tables.issubset(registered_tables)
    # La table "regles" (V1) n'existe plus : les regles vivent en Python
    # (backend/rules/*.py), seule source de verite (CONCEPTION_V2.md §6.4).
    assert "regles" not in registered_tables


def test_dossier_table_has_expected_columns() -> None:
    """La table 'dossiers' doit exposer les colonnes definies dans le modele de donnees."""
    dossier_table = Base.metadata.tables["dossiers"]
    expected_columns = {
        "id",
        "entrepreneur_id",
        "nom_projet",
        "forme_juridique",
        "capital_social",
        "siege_social",
        "date_creation",
        "statut",
    }

    assert expected_columns.issubset(set(dossier_table.columns.keys()))
