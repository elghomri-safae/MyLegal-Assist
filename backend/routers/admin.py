"""Routeur d'administration — consultation en lecture seule des dossiers de
tous les clients (§support MyLegal). Réservé au rôle admin.

Volontairement lecture seule : un admin ne modifie ni n'évalue le dossier
d'un client à sa place (décision actée) — seules la consultation et la
création de comptes entrepreneurs (backend/routers/auth.py) lui sont
ouvertes.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import UtilisateurConnecte, exiger_role
from backend.core.exceptions import DossierIntrouvableError
from backend.schemas.admin import DossierAdminRead
from backend.services import dossier_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dossiers", response_model=list[DossierAdminRead])
def lister_tous_les_dossiers(
    db: Session = Depends(get_db),
    _admin: UtilisateurConnecte = Depends(exiger_role("admin")),
) -> list[DossierAdminRead]:
    """Liste tous les dossiers, tous clients confondus."""
    return dossier_service.lister_tous_admin(db)


@router.get("/dossiers/{dossier_id}", response_model=DossierAdminRead)
def obtenir_un_dossier(
    dossier_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: UtilisateurConnecte = Depends(exiger_role("admin")),
) -> DossierAdminRead:
    """Consulte un dossier précis, quel que soit son propriétaire."""
    try:
        return dossier_service.obtenir_dossier_admin(db, dossier_id)
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
