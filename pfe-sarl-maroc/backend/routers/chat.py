"""Routeur exposant le chatbot juridique (RAG)."""

from __future__ import annotations

import uuid
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import UtilisateurConnecte, obtenir_utilisateur_connecte
from backend.core.exceptions import DossierIntrouvableError
from backend.rag.chunk_store import charger_chunks
from backend.rag.embeddings import ModeleEmbedding, obtenir_modele_embedding
from backend.rag.generation import ClientGroq, ClientLLM
from backend.rag.indexing import IndexChromaDB, IndexVectoriel
from backend.rag.lexical_search import IndexLexicalBM25
from backend.schemas.chat import QuestionInput, ReponseChatbot
from backend.services import chatbot_service

router = APIRouter(prefix="/chat", tags=["chat"])


@lru_cache(maxsize=1)
def obtenir_index_semantique() -> IndexVectoriel:
    """Dépendance FastAPI fournissant l'index vectoriel (ChromaDB), mis en cache."""
    return IndexChromaDB()


@lru_cache(maxsize=1)
def obtenir_index_lexical() -> IndexLexicalBM25:
    """Dépendance FastAPI fournissant l'index lexical BM25.

    Reconstruit en mémoire depuis ``data/chunks/corpus_chunks.json``, généré
    par ``scripts/indexer_corpus.py``. Substituable en test via
    ``app.dependency_overrides``.
    """
    chunks = charger_chunks()
    return IndexLexicalBM25(chunks)


@lru_cache(maxsize=1)
def obtenir_client_llm() -> ClientLLM:
    """Dépendance FastAPI fournissant le client LLM (Groq), mis en cache."""
    return ClientGroq()


@lru_cache(maxsize=1)
def obtenir_modele_embedding_dependance() -> ModeleEmbedding:
    """Dépendance FastAPI fournissant le modèle d'embedding, mis en cache."""
    return obtenir_modele_embedding()


@router.post("", response_model=ReponseChatbot)
def poser_question(
    payload: QuestionInput,
    db: Session = Depends(get_db),
    index_semantique: IndexVectoriel = Depends(obtenir_index_semantique),
    index_lexical: IndexLexicalBM25 = Depends(obtenir_index_lexical),
    client_llm: ClientLLM = Depends(obtenir_client_llm),
    modele_embedding: ModeleEmbedding = Depends(obtenir_modele_embedding_dependance),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> ReponseChatbot:
    """Répond à une question juridique, générale ou contextuelle à un dossier
    (CONCEPTION_V2.md §6) — authentification requise.
    """
    try:
        return chatbot_service.poser_question(
            db,
            uuid.UUID(utilisateur.id),
            payload,
            index_semantique,
            index_lexical,
            client_llm,
            modele_embedding,
        )
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
