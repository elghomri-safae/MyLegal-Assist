

"""Routeur d'inscription et de connexion (Phase 6).

MODIFICATION (Phase 1 — comptes créés par MyLegal) : ``POST /auth/inscription``
(public, ``role`` choisi librement par l'appelant) est retiré. Remplacé par
``POST /auth/entrepreneurs``, protégé par ``exiger_role("admin")`` — déjà
disponible dans ``backend/core/dependencies.py``, jusqu'ici inutilisé par
aucun routeur. Le premier compte admin est créé hors-API, via
``scripts/creer_admin.py`` (jamais de route HTTP pour créer un admin).

``POST /auth/connexion`` est inchangé.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import UtilisateurConnecte, exiger_role
from backend.core.exceptions import AppError
from backend.schemas.auth import (
    EntrepreneurCreation,
    EntrepreneurCree,
    Token,
    UtilisateurConnexion,
)
from backend.services.auth_service import authentifier_utilisateur, creer_entrepreneur

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/entrepreneurs", response_model=EntrepreneurCree, status_code=status.HTTP_201_CREATED
)
def creer_compte_entrepreneur(
    payload: EntrepreneurCreation,
    db: Session = Depends(get_db),
    _admin: UtilisateurConnecte = Depends(exiger_role("admin")),
) -> EntrepreneurCree:
    """Crée un compte entrepreneur — réservé au personnel MyLegal (admin).

    Le mot de passe temporaire généré n'apparaît que dans cette réponse, à
    communiquer au client hors-bande.
    """
    try:
        return creer_entrepreneur(db, payload)
    except AppError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/connexion", response_model=Token)
def connexion(payload: UtilisateurConnexion, db: Session = Depends(get_db)) -> Token:
    """Authentifie un utilisateur et retourne un jeton d'accès JWT."""
    try:
        return authentifier_utilisateur(db, payload)
    except AppError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
