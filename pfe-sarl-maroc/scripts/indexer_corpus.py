"""Script d'indexation offline du corpus documentaire (Phase 5).

Exécute le pipeline complet : extraction -> nettoyage -> chunking ->
embeddings -> indexation ChromaDB, et persiste les chunks (JSON, dans
``data/chunks/``) pour la reconstruction de l'index lexical BM25 au
démarrage de l'API.

Ce script utilise les adaptateurs réels (sentence-transformers, ChromaDB) :
il n'a pas été exécuté de bout en bout dans l'environnement de vérification
de ce projet (dépendances lourdes, voir ARCHITECTURE.md §12). Il est destiné
à être lancé dans l'environnement de déploiement réel, une fois par mise à
jour du corpus.

Usage :
    python -m scripts.indexer_corpus
"""

from __future__ import annotations

from backend.rag.chunk_store import sauvegarder_chunks
from backend.rag.chunking import decouper_corpus
from backend.rag.cleaning import nettoyer_corpus
from backend.rag.embeddings import obtenir_modele_embedding
from backend.rag.extraction import extraire_corpus
from backend.rag.indexing import IndexChromaDB


def indexer_corpus() -> None:
    """Exécute le pipeline d'indexation offline de bout en bout."""
    documents_bruts = extraire_corpus()
    documents_nettoyes = nettoyer_corpus(documents_bruts)
    chunks = decouper_corpus(documents_nettoyes)

    sauvegarder_chunks(chunks)

    modele = obtenir_modele_embedding()
    vecteurs = modele.encoder([chunk.texte for chunk in chunks])

    index = IndexChromaDB()
    index.ajouter(chunks, vecteurs)

    print(
        f"Indexation terminee : {len(chunks)} chunks indexes depuis "
        f"{len(documents_nettoyes)} documents."
    )


if __name__ == "__main__":
    indexer_corpus()
