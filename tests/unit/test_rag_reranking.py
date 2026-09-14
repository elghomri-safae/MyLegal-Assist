"""Test unitaire du reranking (backend/rag/reranking.py)."""

from backend.rag.chunking import ChunkDocument
from backend.rag.hybrid_search import ResultatRechercheHybride
from backend.rag.reranking import reranker


def _resultat(niveau: int, score: float) -> ResultatRechercheHybride:
    chunk = ChunkDocument(
        document_titre=f"Doc niveau {niveau}",
        niveau=niveau,
        type_source="x",
        position=0,
        texte="x",
    )
    return ResultatRechercheHybride(
        chunk=chunk, score_fusion=score, score_semantique=None, score_lexical=None
    )


def test_reranker_priorise_le_niveau_documentaire_a_score_comparable() -> None:
    """A score de fusion quasi identique, le niveau 1 doit passer devant le niveau 3."""
    resultats = [_resultat(niveau=3, score=0.50), _resultat(niveau=1, score=0.49)]

    resultats_rerankes = reranker(resultats)

    assert resultats_rerankes[0].chunk.niveau == 1


def test_reranker_ne_reordonne_pas_si_l_ecart_de_score_est_important() -> None:
    """Un net écart de score de fusion doit l'emporter sur le niveau documentaire."""
    resultats = [_resultat(niveau=1, score=0.10), _resultat(niveau=3, score=0.90)]

    resultats_rerankes = reranker(resultats)

    assert resultats_rerankes[0].chunk.niveau == 3


def test_reranker_gere_une_liste_vide() -> None:
    """Une liste vide doit retourner une liste vide, sans erreur."""
    assert reranker([]) == []
