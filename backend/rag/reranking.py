
"""Reranking des résultats de recherche hybride.

MODIFICATION (intégration corpus juridique) : le cahier des charges impose
explicitement un reranker neuronal, ``BAAI/bge-reranker-v2-m3`` — l'ancienne
implémentation de ce fichier utilisait un heuristique de repli (tri par
``niveau`` documentaire) car "aucun modèle multilingue français fiable
n'avait été identifié avec certitude" ; ce n'est plus le cas, le modèle est
maintenant imposé explicitement. Un cross-encoder évalue directement la
paire (question, texte du chunk) — il n'a donc plus besoin, et ne doit plus
dépendre, d'un ``niveau`` documentaire qui n'existe pas dans le nouveau
corpus (``ChunkDocument.niveau`` reste ``None`` pour ces chunks, cf.
``corpus_loader.py``).

CHANGEMENT DE SIGNATURE (documenté, cf. analyse) : ``reranker()`` prend
maintenant la question en paramètre (un cross-encoder évalue une paire
question/passage, il ne peut pas reclasser à partir des seuls résultats).
Aucun appelant connu (parmi les fichiers fournis) n'utilisait l'ancienne
signature ``reranker(resultats)`` — seul ``rag_pipeline.py`` (nouveau,
écrit avec la nouvelle signature dès le départ) l'appelle. Si un autre
fichier du projet (service, router...) appelle déjà ``reranker``, il faudra
le mettre à jour avec la nouvelle signature.

AJOUT (détection hors-périmètre) : ``reranker()`` triait les candidats puis
jetait leurs scores — aucun signal de confiance n'était donc disponible
pour détecter une question hors du corpus (BM25/recherche vectorielle
renvoient toujours un top-k, même sans rien de pertinent). ``reranker_score``
expose maintenant le score de chaque candidat retenu (sigmoïde appliquée au
score brut du cross-encoder, comme recommandé par la fiche du modèle
BAAI/bge-reranker-v2-m3, pour obtenir une valeur bornée [0, 1] plutôt qu'un
logit non borné) ; ``rag_pipeline.py`` s'en sert pour couper l'appel à Groq
si le meilleur score est trop bas. ``reranker()`` est conservée telle
quelle (même signature, même comportement) pour ne rien casser.

MODIFICATION (contention CPU sous requêtes concurrentes) : observé en
conditions réelles — un seul reranking prend déjà ~1 minute sur CPU (pas de
GPU disponible), mais quand 2-3 requêtes appellent le reranker en même
temps (FastAPI exécute les dépendances synchrones dans un threadpool, donc
plusieurs inférences PyTorch tournent réellement en parallèle), le temps
par lot explose à 8-9 MINUTES au lieu de s'additionner simplement — la
contention CPU (cache thrashing, changement de contexte constant) rend
l'exécution concurrente largement plus lente que l'exécution séquentielle
pour ce type de charge CPU-bound. ``_VERROU_RERANKER`` sérialise les appels
au modèle : une requête attend son tour au lieu de se battre pour le CPU
avec les autres, ce qui est nettement plus rapide en pratique dans ce cas
précis, même si cela introduit une file d'attente.
"""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from backend.rag.hybrid_search import ResultatRechercheHybride

NOM_MODELE_PAR_DEFAUT = "BAAI/bge-reranker-v2-m3"

# Un seul reranking à la fois : cf. note de module sur la contention CPU.
_VERROU_RERANKER = threading.Lock()
SEUIL_CONFIANCE_PAR_DEFAUT = 0.60

class ModeleReranker(Protocol):
    """Interface minimale attendue d'un modèle de reranking (cross-encoder)."""

    def scorer(self, question: str, textes: list[str]) -> list[float]:
        """Retourne un score de pertinence (plus haut = plus pertinent)
        pour chaque texte, évalué conjointement avec la question."""
        ...


class ModeleBGEReranker:
    """Adaptateur sentence-transformers (CrossEncoder) implémentant ``ModeleReranker``."""

    def __init__(self, nom_modele: str = NOM_MODELE_PAR_DEFAUT) -> None:
        from sentence_transformers import CrossEncoder  # import différé

        self._modele = CrossEncoder(nom_modele)

    def scorer(self, question: str, textes: list[str]) -> list[float]:
        if not textes:
            return []
        paires = [(question, texte) for texte in textes]
        # Sérialisé : cf. note de module (contention CPU sous requêtes
        # concurrentes, régression réelle observée : 56s -> 8-9min).
        with _VERROU_RERANKER:
            scores = self._modele.predict(paires)
        return [float(score) for score in scores]


@lru_cache(maxsize=1)
def obtenir_modele_reranker() -> ModeleBGEReranker:
    """Retourne une instance partagée du reranker (chargement coûteux, mis en cache)."""
    return ModeleBGEReranker()


def _sigmoide(x: float) -> float:
    """Convertit le score brut (logit, non borné) du cross-encoder en une
    valeur [0, 1] interprétable comme une confiance de pertinence — la
    fiche du modèle BAAI/bge-reranker-v2-m3 recommande explicitement cette
    transformation avant tout seuillage (le score brut, lui, n'est PAS
    directement comparable à un seuil du type "0.5")."""
    return 1.0 / (1.0 + math.exp(-x))


@dataclass(frozen=True)
class ResultatReranking:
    """Un résultat reclassé, avec son score de confiance [0, 1]."""

    resultat: ResultatRechercheHybride
    score: float


def reranker_score(
    question: str,
    resultats: list[ResultatRechercheHybride],
    modele: ModeleReranker,
) -> list[ResultatReranking]:
    """Reclasse TOUS les candidats (pas de troncature ``k`` ici) et expose
    le score de confiance de chacun — à utiliser quand ce score est
    nécessaire en aval (ex. détection hors-périmètre). Pour le cas simple
    "juste les k meilleurs chunks", utiliser ``reranker()``."""
    if not resultats:
        return []

    textes = [resultat.chunk.texte for resultat in resultats]
    scores_bruts = modele.scorer(question, textes)

    paires = list(zip(resultats, scores_bruts, strict=True))
    paires.sort(key=lambda paire: paire[1], reverse=True)

    return [
        ResultatReranking(resultat=resultat, score=_sigmoide(score_brut))
        for resultat, score_brut in paires
    ]


def reranker(
    question: str,
    resultats: list[ResultatRechercheHybride],
    modele: ModeleReranker,
    k: int = 8,
) -> list[ResultatRechercheHybride]:
    """Reclasse les candidats issus de la recherche hybride avec un
    cross-encoder (question, texte du chunk), et conserve les ``k`` meilleurs.

    Ne dépend d'aucune information de hiérarchie documentaire (``niveau``) :
    le score du cross-encoder est la seule base du classement.

    Ne retourne pas les scores (cf. ``reranker_score`` si nécessaire) :
    conservée telle quelle pour compatibilité avec tout appelant existant.
    """
    return [item.resultat for item in reranker_score(question, resultats, modele)[:k]]
