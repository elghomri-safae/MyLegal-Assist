"""Tests unitaires du découpage en chunks (backend/rag/chunking.py)."""

from backend.rag.chunking import decouper_corpus, decouper_document
from backend.rag.cleaning import DocumentNettoye


def test_decouper_document_produit_des_chunks_avec_metadonnees() -> None:
    """Chaque chunk doit conserver les métadonnées du document source."""
    document = DocumentNettoye(
        titre="Doc Test",
        niveau=1,
        type_source="texte_de_loi",
        texte="Phrase un. " * 200,
    )

    chunks = decouper_document(document)

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.document_titre == "Doc Test"
        assert chunk.niveau == 1
        assert chunk.type_source == "texte_de_loi"
        assert chunk.texte.strip() != ""


def test_decouper_document_positions_sequentielles() -> None:
    """Les positions des chunks d'un même document doivent être 0, 1, 2, ..."""
    document = DocumentNettoye(
        titre="Doc Test", niveau=1, type_source="texte_de_loi", texte="Phrase un. " * 200
    )

    chunks = decouper_document(document)

    assert [chunk.position for chunk in chunks] == list(range(len(chunks)))


def test_decouper_corpus_agrege_tous_les_documents() -> None:
    """decouper_corpus doit agréger les chunks de tous les documents fournis."""
    documents = [
        DocumentNettoye(titre="A", niveau=1, type_source="texte_de_loi", texte="Alpha. " * 50),
        DocumentNettoye(titre="B", niveau=2, type_source="source_officielle", texte="Beta. " * 50),
    ]

    chunks = decouper_corpus(documents)

    titres = {chunk.document_titre for chunk in chunks}
    assert titres == {"A", "B"}
