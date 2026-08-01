"""Routeur exposant le cycle de vie persistant d'un dossier de création
(CONCEPTION_V2.md §2, §4, §5, §9) et son évaluation par le système expert.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import UtilisateurConnecte, obtenir_utilisateur_connecte
from backend.core.exceptions import DossierIntrouvableError
from backend.schemas.dossier import DossierCreate, DossierRead, DossierUpdate, IdentitePersonneInput
from backend.schemas.evaluation import EvaluationRead
from backend.services import dossier_service

router = APIRouter(prefix="/dossiers", tags=["dossiers"])


@router.post("", response_model=DossierRead, status_code=status.HTTP_201_CREATED)
def creer_dossier(
    payload: DossierCreate,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> DossierRead:
    """Crée un nouveau dossier (CONCEPTION_V2.md §2, étape 3)."""
    return dossier_service.creer_dossier(db, uuid.UUID(utilisateur.id), payload)


@router.get("", response_model=list[DossierRead])
def lister_dossiers(
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> list[DossierRead]:
    """Tableau de bord : liste des dossiers de l'utilisateur connecté (§9.1)."""
    return dossier_service.lister_dossiers(db, uuid.UUID(utilisateur.id))


@router.get("/{dossier_id}", response_model=DossierRead)
def obtenir_dossier(
    dossier_id: uuid.UUID,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> DossierRead:
    try:
        return dossier_service.obtenir_dossier(db, dossier_id, uuid.UUID(utilisateur.id))
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.patch("/{dossier_id}", response_model=DossierRead)
def mettre_a_jour_dossier(
    dossier_id: uuid.UUID,
    payload: DossierUpdate,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> DossierRead:
    """Remplissage progressif du dossier (CONCEPTION_V2.md §2, §8 niveau 1 :
    la validation structurelle est déjà appliquée par les contraintes
    Pydantic de ``DossierUpdate`` avant d'atteindre ce point).
    """
    try:
        return dossier_service.mettre_a_jour_dossier(
            db, dossier_id, uuid.UUID(utilisateur.id), payload
        )
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.post(
    "/{dossier_id}/identites", response_model=DossierRead, status_code=status.HTTP_201_CREATED
)
def ajouter_identite(
    dossier_id: uuid.UUID,
    payload: IdentitePersonneInput,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> DossierRead:
    """Ajoute une identité d'associé au dossier (saisie manuelle uniquement,
    module OCR supprimé — CONCEPTION_V2.md §7)."""
    try:
        return dossier_service.ajouter_identite(db, dossier_id, uuid.UUID(utilisateur.id), payload)
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.post(
    "/{dossier_id}/evaluer", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED
)
def evaluer_dossier(
    dossier_id: uuid.UUID,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> EvaluationRead:
    """Déclenche une évaluation par le système expert et la persiste
    (CONCEPTION_V2.md §5) : peut être appelé autant de fois que nécessaire,
    chaque appel enrichit l'historique du dossier sans écraser le précédent.
    """
    try:
        return dossier_service.evaluer_et_persister(db, dossier_id, uuid.UUID(utilisateur.id))
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get("/{dossier_id}/evaluations", response_model=list[EvaluationRead])
def lister_evaluations(
    dossier_id: uuid.UUID,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
) -> list[EvaluationRead]:
    """Historique complet des évaluations d'un dossier (CONCEPTION_V2.md §9.4)."""
    try:
        return dossier_service.lister_evaluations(db, dossier_id, uuid.UUID(utilisateur.id))
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
