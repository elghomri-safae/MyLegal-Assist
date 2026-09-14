"""Routeur exposant le cycle de vie persistant d'un dossier de création
(CONCEPTION_V2.md §2, §4, §5, §9) et son évaluation par le système expert.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import UtilisateurConnecte, exiger_role, obtenir_utilisateur_connecte
from backend.core.exceptions import DossierIntrouvableError, IdentiteDupliqueeError
from backend.schemas.dossier import DossierCreate, DossierRead, DossierUpdate, IdentitePersonneInput
from backend.schemas.evaluation import EvaluationRead
from backend.services import dossier_service

router = APIRouter(prefix="/dossiers", tags=["dossiers"])

from backend.core.exceptions import (
    DossierIntrouvableError,
    IdentiteDupliqueeError,
    IdentiteIntrouvableError,
)
from backend.schemas.dossier import (
    DossierCreate,
    DossierRead,
    DossierUpdate,
    IdentitePersonneInput,
    IdentitePersonneUpdate,
)
from backend.constants.document_classification import CLASSIFICATION_PIECES
from backend.schemas.dossier import ClassificationPieceRead


@router.get("/classification-pieces", response_model=list[ClassificationPieceRead])
def lister_classification_pieces() -> list[ClassificationPieceRead]:
    """Expose la classification client/cabinet des pièces, pour que le
    frontend n'ait jamais à dupliquer cette logique métier (cf. incident
    CAP-002 : deux sources indépendantes du même choix avaient divergé)."""
    return [
        ClassificationPieceRead(
            type_piece=type_piece,
            responsable=classification.responsable,
            label=classification.label,
        )
        for type_piece, classification in CLASSIFICATION_PIECES.items()
    ]

@router.patch("/{dossier_id}/identites/{identite_id}", response_model=DossierRead)
def modifier_identite(
    dossier_id: uuid.UUID,
    identite_id: uuid.UUID,
    payload: IdentitePersonneUpdate,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(exiger_role("entrepreneur")),
) -> DossierRead:
    """Modifie un associé déjà enregistré (remplissage progressif ou correction)."""
    try:
        return dossier_service.modifier_identite(
            db, dossier_id, uuid.UUID(utilisateur.id), identite_id, payload
        )
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except IdentiteIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IdentiteDupliqueeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{dossier_id}/identites/{identite_id}", response_model=DossierRead)
def supprimer_identite(
    dossier_id: uuid.UUID,
    identite_id: uuid.UUID,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(exiger_role("entrepreneur")),
) -> DossierRead:
    """Retire un associé du dossier."""
    try:
        return dossier_service.supprimer_identite(
            db, dossier_id, uuid.UUID(utilisateur.id), identite_id
        )
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except IdentiteIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    
@router.post("", response_model=DossierRead, status_code=status.HTTP_201_CREATED)
def creer_dossier(
    payload: DossierCreate,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(exiger_role("entrepreneur")),
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
    utilisateur: UtilisateurConnecte = Depends(exiger_role("entrepreneur")),
) -> DossierRead:
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
    utilisateur: UtilisateurConnecte = Depends(exiger_role("entrepreneur")),
) -> DossierRead:
    """Ajoute une identité d'associé au dossier (saisie manuelle uniquement,
    module OCR supprimé — CONCEPTION_V2.md §7)."""
    try:
        return dossier_service.ajouter_identite(db, dossier_id, uuid.UUID(utilisateur.id), payload)
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except IdentiteDupliqueeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/{dossier_id}/evaluer", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED
)
def evaluer_dossier(
    dossier_id: uuid.UUID,
    db: Session = Depends(get_db),
    utilisateur: UtilisateurConnecte = Depends(exiger_role("entrepreneur")),
) -> EvaluationRead:
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
    try:
        return dossier_service.lister_evaluations(db, dossier_id, uuid.UUID(utilisateur.id))
    except DossierIntrouvableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc