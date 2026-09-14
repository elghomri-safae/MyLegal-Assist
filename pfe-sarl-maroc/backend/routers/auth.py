"""Routeur d'inscription et de connexion (Phase 6)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.exceptions import AppError
from backend.schemas.auth import (
    Token,
    UtilisateurConnexion,
    UtilisateurInscription,
    UtilisateurPublic,
)
from backend.services.auth_service import authentifier_utilisateur, inscrire_utilisateur

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/inscription", response_model=UtilisateurPublic, status_code=status.HTTP_201_CREATED)
def inscription(
    payload: UtilisateurInscription, db: Session = Depends(get_db)
) -> UtilisateurPublic:
    """Inscrit un nouvel utilisateur (entrepreneur ou admin)."""
    try:
        return inscrire_utilisateur(db, payload)
    except AppError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/connexion", response_model=Token)
def connexion(payload: UtilisateurConnexion, db: Session = Depends(get_db)) -> Token:
    """Authentifie un utilisateur et retourne un jeton d'accès JWT."""
    try:
        return authentifier_utilisateur(db, payload)
    except AppError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
