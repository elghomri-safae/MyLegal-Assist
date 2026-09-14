"""Pipeline RAG (chatbot juridique) — Phase 5.

Modules (pipeline d'indexation, offline, exécuté par scripts/indexer_corpus.py) :
- ``extraction`` : lecture des documents bruts du corpus fermé (data/raw/).
- ``cleaning`` : nettoyage textuel.
- ``chunking`` : découpage en chunks indexables (LangChain).
- ``chunk_store`` : sérialisation des chunks (utilisée par l'index lexical).
- ``embeddings`` : génération des vecteurs d'embedding (sentence-transformers).
- ``indexing`` : indexation/recherche vectorielle (ChromaDB).

Modules (pipeline de requête, exécuté à chaque question) :
- ``lexical_search`` : recherche lexicale BM25 (pur Python).
- ``hybrid_search`` : fusion des résultats sémantiques et lexicaux (RRF).
- ``reranking`` : re-priorisation selon la hiérarchie des sources.
- ``generation`` : génération de la réponse avec citations (Groq).

Orchestration complète dans ``backend/services/rag_service.py``.
"""
