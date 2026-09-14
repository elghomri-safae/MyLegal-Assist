"""Tests unitaires de l'extraction du corpus (backend/rag/extraction.py)."""

from backend.rag.extraction import CATALOGUE_CORPUS, extraire_corpus


def test_catalogue_corpus_contient_les_six_documents_fermes() -> None:
    """Le corpus fermé doit contenir exactement les 6 documents S1 à S6."""
    assert len(CATALOGUE_CORPUS) == 6
    niveaux = {document.niveau for document in CATALOGUE_CORPUS}
    assert niveaux == {1, 2, 3}


def test_extraire_corpus_lit_reellement_les_fichiers() -> None:
    """extraire_corpus doit retourner un texte non vide pour chaque document."""
    resultats = extraire_corpus()

    assert len(resultats) == 6
    for document, texte in resultats:
        assert texte.strip() != ""
        assert document.titre != ""
