"""Recherche lexicale (BM25) pour la composante lexicale de la recherche hybride.

Implémentation pure Python, sans dépendance supplémentaire : la stack
imposée par le cahier des charges ne prévoit pas de bibliothèque de
recherche lexicale dédiée (voir DECISIONS.md, Phase 5). BM25 est une
formule bien établie (Robertson & Zaragoza) et suffisamment simple pour
être implémentée directement plutôt que d'ajouter une dépendance non
imposée.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from backend.rag.chunking import ChunkDocument

_MOTIF_MOT = re.compile(r"[a-zàâäéèêëïîôöùûüç0-9]+", re.IGNORECASE)

K1 = 1.5
B = 0.75


def _tokeniser(texte: str) -> list[str]:
    return _MOTIF_MOT.findall(texte.lower())


@dataclass(frozen=True)
class ResultatRechercheLexicale:
    """Un résultat de recherche lexicale, avec son score BM25."""

    chunk: ChunkDocument
    score: float


class IndexLexicalBM25:
    """Index lexical BM25 construit en mémoire à partir d'une liste de chunks."""

    def __init__(self, chunks: list[ChunkDocument]) -> None:
        self._chunks = chunks
        self._documents_tokenises = [_tokeniser(chunk.texte) for chunk in chunks]
        self._longueurs = [len(doc) for doc in self._documents_tokenises]
        self._longueur_moyenne = (
            sum(self._longueurs) / len(self._longueurs) if self._longueurs else 0.0
        )
        self._nb_documents = len(chunks)
        self._frequences_documents = self._construire_frequences_documents()

    def _construire_frequences_documents(self) -> dict[str, int]:
        frequences: dict[str, int] = {}
        for tokens in self._documents_tokenises:
            for terme in set(tokens):
                frequences[terme] = frequences.get(terme, 0) + 1
        return frequences

    def _idf(self, terme: str) -> float:
        df = self._frequences_documents.get(terme, 0)
        return math.log(1 + (self._nb_documents - df + 0.5) / (df + 0.5))

    def rechercher(self, requete: str, k: int) -> list[ResultatRechercheLexicale]:
        """Retourne les k chunks avec le meilleur score BM25 pour la requête."""
        termes_requete = _tokeniser(requete)
        scores: list[float] = []

        for position, tokens in enumerate(self._documents_tokenises):
            compteur = Counter(tokens)
            longueur_doc = self._longueurs[position]
            score = 0.0
            for terme in termes_requete:
                freq = compteur.get(terme, 0)
                if freq == 0:
                    continue
                idf = self._idf(terme)
                denominateur = freq + K1 * (
                    1 - B + B * longueur_doc / (self._longueur_moyenne or 1)
                )
                score += idf * (freq * (K1 + 1)) / denominateur
            scores.append(score)

        classement = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        return [
            ResultatRechercheLexicale(chunk=self._chunks[position], score=scores[position])
            for position in classement
            if scores[position] > 0
        ]
