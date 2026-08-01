"""Reranking des résultats de recherche hybride.

Plutôt qu'un reranker neuronal (cross-encoder) — pour lequel aucun modèle
multilingue français fiable n'a été identifié avec certitude dans la stack
imposée, et qu'il serait risqué d'affirmer sans vérification (Règle absolue
n°1) — le reranking applique un signal documentaire explicite et
vérifiable : à score de fusion comparable, un extrait de niveau
documentaire plus élevé (1 > 2 > 3, cf. hiérarchie des sources du corpus,
PROJECT.md) est priorisé.
"""

from __future__ import annotations

from backend.rag.hybrid_search import ResultatRechercheHybride

SEUIL_ECART_SCORE_COMPARABLE = 0.02


def _cle_tri(resultat: ResultatRechercheHybride, meilleur_score: float) -> tuple[int, int, float]:
    ecart = meilleur_score - resultat.score_fusion
    if ecart <= SEUIL_ECART_SCORE_COMPARABLE:
        # Groupe des resultats "comparables" au meilleur score : priorite au
        # niveau documentaire, puis au score.
        return (0, resultat.chunk.niveau, -resultat.score_fusion)
    # Groupe des resultats nettement moins bien classes : seul le score compte.
    return (1, 0, -resultat.score_fusion)


def reranker(resultats: list[ResultatRechercheHybride]) -> list[ResultatRechercheHybride]:
    """Réordonne les résultats : priorité au niveau documentaire à score comparable."""
    if not resultats:
        return []
    meilleur_score = max(resultat.score_fusion for resultat in resultats)
    return sorted(resultats, key=lambda r: _cle_tri(r, meilleur_score))
