"""Test unitaire de la fusion RRF (backend/rag/hybrid_search.py)."""

from backend.rag.chunking import ChunkDocument
from backend.rag.hybrid_search import fusionner_resultats
from backend.rag.indexing import ResultatRechercheSemantique
from backend.rag.lexical_search import ResultatRechercheLexicale


def _chunk(titre: str, position: int) -> ChunkDocument:
    return ChunkDocument(
        document_titre=titre, niveau=1, type_source="texte_de_loi", position=position, texte="x"
    )


def test_fusion_priorise_un_chunk_present_dans_les_deux_classements() -> None:
    """Un chunk bien classé dans les deux recherches doit dominer la fusion."""
    chunk_commun = _chunk("Doc A", 0)
    chunk_semantique_seul = _chunk("Doc B", 1)
    chunk_lexical_seul = _chunk("Doc C", 2)

    resultats_semantiques = [
        ResultatRechercheSemantique(identifiant="s0", chunk=chunk_commun, score=0.9),
        ResultatRechercheSemantique(identifiant="s1", chunk=chunk_semantique_seul, score=0.8),
    ]
    resultats_lexicaux = [
        ResultatRechercheLexicale(chunk=chunk_commun, score=5.0),
        ResultatRechercheLexicale(chunk=chunk_lexical_seul, score=4.0),
    ]

    resultats_fusionnes = fusionner_resultats(resultats_semantiques, resultats_lexicaux)

    assert resultats_fusionnes[0].chunk.document_titre == "Doc A"
    assert resultats_fusionnes[0].score_semantique == 0.9
    assert resultats_fusionnes[0].score_lexical == 5.0


def test_fusion_conserve_les_chunks_presents_dans_un_seul_classement() -> None:
    """Un chunk présent dans un seul classement doit apparaître dans le résultat fusionné."""
    resultats_semantiques = [
        ResultatRechercheSemantique(identifiant="s0", chunk=_chunk("Doc A", 0), score=0.5)
    ]
    resultats_lexicaux: list[ResultatRechercheLexicale] = []

    resultats_fusionnes = fusionner_resultats(resultats_semantiques, resultats_lexicaux)

    assert len(resultats_fusionnes) == 1
    assert resultats_fusionnes[0].score_lexical is None
