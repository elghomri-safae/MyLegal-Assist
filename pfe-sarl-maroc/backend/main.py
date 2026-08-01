"""FastAPI application entrypoint."""

from fastapi import FastAPI

from backend.config.settings import get_settings
from backend.core.logging import configure_logging
from backend.routers.auth import router as auth_router
from backend.routers.chat import router as chat_router
from backend.routers.dossier import router as dossier_router
from backend.routers.health import router as health_router

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(dossier_router)
app.include_router(chat_router)
