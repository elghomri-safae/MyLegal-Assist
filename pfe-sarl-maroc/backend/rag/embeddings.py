"""Génération d'embeddings pour les chunks du corpus et pour les questions.

Le modèle réel (sentence-transformers, multilingual-e5-large — imposé par le
cahier des charges) est encapsulé derrière le protocole ``ModeleEmbedding`` :
import différé à l'instanciation, substitution possible par un modèle factice
en test, sans charger les poids réels (dépendance lourde, non exercée dans cet
environnement de vérification — voir ARCHITECTURE.md §12).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Protocol

Vecteur = tuple[float, ...]

NOM_MODELE_PAR_DEFAUT = "intfloat/multilingual-e5-large"


class ModeleEmbedding(Protocol):
    """Interface minimale attendue d'un modèle d'embeddings."""

    def encoder(self, textes: list[str]) -> list[Vecteur]:
        """Retourne un vecteur d'embedding pour chaque texte fourni."""
        ...


class ModeleSentenceTransformer:
    """Adaptateur sentence-transformers implémentant ``ModeleEmbedding``."""

    def __init__(self, nom_modele: str = NOM_MODELE_PAR_DEFAUT) -> None:
        from sentence_transformers import SentenceTransformer  # import différé

        self._modele = SentenceTransformer(nom_modele)

    def encoder(self, textes: list[str]) -> list[Vecteur]:
        vecteurs = self._modele.encode(textes, normalize_embeddings=True)
        return [tuple(float(valeur) for valeur in vecteur) for vecteur in vecteurs]


@lru_cache(maxsize=1)
def obtenir_modele_embedding() -> ModeleSentenceTransformer:
    """Retourne une instance partagée du modèle d'embedding (chargement coûteux, mis en cache)."""
    return ModeleSentenceTransformer()
