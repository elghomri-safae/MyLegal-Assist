
"""Génération d'embeddings pour les chunks du corpus et pour les questions.

Le modèle réel (sentence-transformers, multilingual-e5-large — imposé par le
cahier des charges) est encapsulé derrière le protocole ``ModeleEmbedding`` :
import différé à l'instanciation, substitution possible par un modèle factice
en test, sans charger les poids réels (dépendance lourde, non exercée dans cet
environnement de vérification — voir ARCHITECTURE.md §12).

MODIFICATION (intégration corpus juridique) : les modèles de la famille E5
(dont ``intfloat/multilingual-e5-large``) exigent un préfixe différent selon
qu'on encode une requête ou un passage (cf. carte du modèle E5) — sans ce
préfixe, la qualité de la similarité cosinus se dégrade sensiblement. Les
deux fonctions ``encoder_requete``/``encoder_passages`` ci-dessous
l'appliquent systématiquement, plutôt que de compter sur chaque appelant
pour s'en souvenir. ``ModeleEmbedding.encoder`` (sans préfixe) reste
disponible tel quel pour ne rien casser côté appelants existants.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Protocol

Vecteur = tuple[float, ...]

NOM_MODELE_PAR_DEFAUT = "intfloat/multilingual-e5-large"

PREFIXE_REQUETE = "query: "
PREFIXE_PASSAGE = "passage: "


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
# Cela réduit chaque vecteur à une norme de 1. 
# Cela permet d'utiliser la similarité cosinus comme mesure de distance, 
# qui est plus naturelle pour comparer du texte.
# Comparaison : Sans normalisation, la similarité cosinus n'est pas stable (la longueur des vecteurs varie).
#  Avec normalisation, le cosinus devient directement interprétable en pourcentage de similarité.
        return [tuple(float(valeur) for valeur in vecteur) for vecteur in vecteurs]


@lru_cache(maxsize=1)
def obtenir_modele_embedding() -> ModeleSentenceTransformer:
    """Retourne une instance partagée du modèle d'embedding (chargement coûteux, mis en cache)."""
    return ModeleSentenceTransformer()
# Le modèle E5 est lourd (environ 2-3 Go en mémoire). Le charger une seule fois et le réutiliser évite de le recharger à chaque requête.
# Comparaison : Sans cache, chaque requête prendrait 5-10 secondes de plus (le temps de charger le modèle). Avec cache, le modèle est déjà en mémoire.


def encoder_requete(question: str, modele: ModeleEmbedding) -> Vecteur:
    """Encode une question utilisateur avec le préfixe E5 ``"query: "``."""
    return modele.encoder([PREFIXE_REQUETE + question])[0]


def encoder_passages(textes: list[str], modele: ModeleEmbedding) -> list[Vecteur]:
    """Encode des passages (chunks du corpus) avec le préfixe E5 ``"passage: "``."""
    if not textes:
        return []
    return modele.encoder([PREFIXE_PASSAGE + texte for texte in textes])
