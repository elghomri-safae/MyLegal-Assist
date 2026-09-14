"""Test unitaire de la recherche lexicale BM25 (backend/rag/lexical_search.py)."""

from backend.rag.chunking import ChunkDocument
from backend.rag.lexical_search import IndexLexicalBM25


def _chunk(texte: str, position: int) -> ChunkDocument:
    return ChunkDocument(
        document_titre="Doc Test",
        niveau=1,
        type_source="texte_de_loi",
        position=position,
        texte=texte,
    )


def test_bm25_retourne_le_chunk_le_plus_pertinent_en_premier() -> None:
    """Le chunk contenant les termes de la requête doit être classé avant les autres."""
    chunks = [
        _chunk("Le capital social minimum de la SARL est librement fixe.", 0),
        _chunk("Les formalites de blocage bancaire concernent le capital social eleve.", 1),
        _chunk("La CNSS gere l'affiliation des salaries.", 2),
    ]
    index = IndexLexicalBM25(chunks)

    resultats = index.rechercher("blocage bancaire capital", k=3)

    assert resultats
    assert resultats[0].chunk.position == 1


def test_bm25_ne_retourne_pas_de_chunk_sans_terme_commun() -> None:
    """Un chunk sans aucun terme en commun avec la requête ne doit pas être retourné."""
    chunks = [_chunk("La CNSS gere l'affiliation des salaries.", 0)]
    index = IndexLexicalBM25(chunks)

    resultats = index.rechercher("certificat negatif", k=3)

    assert resultats == []
