
"""FastAPI application entrypoint.

MODIFICATION (préchargement du pipeline RAG) : sans ceci, les dépendances
lourdes (embeddings, reranker, index vectoriel/lexical) ne se chargent
qu'à la toute première question posée par un utilisateur après un
(re)démarrage — un délai réel de 60-180s déjà observé en conditions
réelles (timeout Streamlit). Le ``lifespan`` ci-dessous précharge ces
mêmes dépendances (identiques, même objets ``@lru_cache``, donc même
cache) une seule fois au démarrage d'uvicorn, avant qu'aucune requête ne
soit servie.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config.settings import get_settings
from backend.core.logging import configure_logging
from backend.routers.admin import router as admin_router
from backend.routers.auth import router as auth_router
from backend.routers.chat import (
    obtenir_client_llm,
    obtenir_client_reranker,
    obtenir_index_lexical,
    obtenir_index_semantique,
    obtenir_modele_embedding_dependance,
)
from backend.routers.chat import router as chat_router
from backend.routers.dossier import router as dossier_router
from backend.routers.health import router as health_router

configure_logging()
settings = get_settings()
logger = logging.getLogger(__name__)

# (nom_affiche, fonction_a_precharger) — chaque fonction est le MÊME objet
# @lru_cache(maxsize=1) que celui injecté via Depends(...) sur les routes de
# backend/routers/chat.py : l'appeler ici peuple ce cache une fois pour
# toutes, la première vraie requête utilisateur le trouve déjà chaud.
_DEPENDANCES_A_PRECHARGER = (
    ("modèle d'embedding (multilingual-e5-large)", obtenir_modele_embedding_dependance),
    ("reranker (bge-reranker-v2-m3)", obtenir_client_reranker),
    ("index vectoriel (ChromaDB)", obtenir_index_semantique),
    ("index lexical (BM25)", obtenir_index_lexical),
    ("client LLM (Groq)", obtenir_client_llm),
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Préchargement des dépendances du pipeline RAG...")
    for nom, precharger in _DEPENDANCES_A_PRECHARGER:
        try:
            precharger()
            logger.info("  ✓ %s", nom)
        except Exception:
            # Dégradation gracieuse : un échec de préchargement (modèle
            # manquant, service indisponible au démarrage...) ne doit pas
            # empêcher l'API de démarrer — la dépendance sera simplement
            # rechargée (et l'erreur re-levée si toujours en échec) au
            # premier appel réel, comme avant ce changement.
            logger.exception("  ✗ Échec du préchargement : %s (rechargement au premier appel)", nom)
    logger.info("Préchargement terminé.")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(dossier_router)
app.include_router(admin_router)
app.include_router(chat_router)
