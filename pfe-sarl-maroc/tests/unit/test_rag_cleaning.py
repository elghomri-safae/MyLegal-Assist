"""Tests unitaires du nettoyage textuel (backend/rag/cleaning.py)."""

from backend.rag.cleaning import nettoyer_document, nettoyer_texte
from backend.rag.extraction import DocumentBrut


def test_nettoyer_texte_reduit_les_espaces_multiples() -> None:
    """Les espaces et tabulations multiples doivent être réduits à un seul espace."""
    assert nettoyer_texte("Bonjour    le\t\tmonde") == "Bonjour le monde"


def test_nettoyer_texte_reduit_les_lignes_vides_multiples() -> None:
    """Trois sauts de ligne consécutifs ou plus doivent être réduits à deux."""
    resultat = nettoyer_texte("Paragraphe 1\n\n\n\nParagraphe 2")
    assert resultat == "Paragraphe 1\n\nParagraphe 2"


def test_nettoyer_document_conserve_les_metadonnees() -> None:
    """nettoyer_document doit conserver titre, niveau et type_source du document."""
    document = DocumentBrut(
        titre="Doc Test", niveau=2, type_source="source_officielle", nom_fichier="x.txt"
    )

    resultat = nettoyer_document(document, "texte   brut")

    assert resultat.titre == "Doc Test"
    assert resultat.niveau == 2
    assert resultat.type_source == "source_officielle"
    assert resultat.texte == "texte brut"
