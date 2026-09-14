"""Recherche hybride : fusion des résultats sémantiques et lexicaux.

La fusion utilise la Reciprocal Rank Fusion (RRF, Cormack et al., 2009), qui
combine deux classements sans nécessiter de normaliser des scores
d'échelles différentes (similarité cosinus vs score BM25) : chaque élément
reçoit 1/(k + rang) dans chaque classement où il apparaît.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.rag.chunking import ChunkDocument
from backend.rag.indexing import ResultatRechercheSemantique
from backend.rag.lexical_search import ResultatRechercheLexicale

CONSTANTE_RRF = 60  # constante usuelle de la formule RRF


@dataclass(frozen=True)
class ResultatRechercheHybride:
    """Un chunk retenu par la fusion des deux recherches, avec son score combiné."""

    chunk: ChunkDocument
    score_fusion: float
    score_semantique: float | None
    score_lexical: float | None


def _cle_chunk(chunk: ChunkDocument) -> tuple[str, int]:
    return (chunk.document_titre, chunk.position)


def fusionner_resultats(
    resultats_semantiques: list[ResultatRechercheSemantique],
    resultats_lexicaux: list[ResultatRechercheLexicale],
) -> list[ResultatRechercheHybride]:
    """Fusionne deux classements (sémantique, lexical) par Reciprocal Rank Fusion."""
    scores_fusion: dict[tuple[str, int], float] = {}
    chunks_par_cle: dict[tuple[str, int], ChunkDocument] = {}
    scores_semantiques: dict[tuple[str, int], float] = {}
    scores_lexicaux: dict[tuple[str, int], float] = {}

    for rang, resultat_semantique in enumerate(resultats_semantiques, start=1):
        cle = _cle_chunk(resultat_semantique.chunk)
        chunks_par_cle[cle] = resultat_semantique.chunk
        scores_semantiques[cle] = resultat_semantique.score
        scores_fusion[cle] = scores_fusion.get(cle, 0.0) + 1.0 / (CONSTANTE_RRF + rang)

    for rang, resultat_lexical in enumerate(resultats_lexicaux, start=1):
        cle = _cle_chunk(resultat_lexical.chunk)
        chunks_par_cle[cle] = resultat_lexical.chunk
        scores_lexicaux[cle] = resultat_lexical.score
        scores_fusion[cle] = scores_fusion.get(cle, 0.0) + 1.0 / (CONSTANTE_RRF + rang)

    resultats = [
        ResultatRechercheHybride(
            chunk=chunks_par_cle[cle],
            score_fusion=score,
            score_semantique=scores_semantiques.get(cle),
            score_lexical=scores_lexicaux.get(cle),
        )
        for cle, score in scores_fusion.items()
    ]

    return sorted(resultats, key=lambda r: r.score_fusion, reverse=True)
