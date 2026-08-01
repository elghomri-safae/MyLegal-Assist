"""Health-check endpoint used to verify the API and its database are up."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck(db: Session = Depends(get_db)) -> dict[str, str]:
    """Retourne l'etat de l'API et de sa connexion a la base de donnees."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
