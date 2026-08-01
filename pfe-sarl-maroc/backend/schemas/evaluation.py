"""Schémas Pydantic du verdict produit par le système expert anti-rejet."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from backend.models.enums import StatutGlobalEnum


class AnomalieResult(BaseModel):
    """Une anomalie détectée par une règle, avec sa justification traçable."""

    id: str
    regle_id: str
    categorie: str
    gravite: str
    message: str
    justification: str
    reference_documentaire: str
    niveau_documentaire: int


class VerdictDossier(BaseModel):
    """Verdict global d'une évaluation de dossier."""

    statut_global: StatutGlobalEnum
    anomalies: list[AnomalieResult]


class EvaluationRead(BaseModel):
    """Une évaluation persistée, telle que consultable dans l'historique d'un
    dossier (CONCEPTION_V2.md §9.4). Sans snapshot des champs du dossier
    (§4.3) : les anomalies suffisent à comprendre a posteriori le verdict.
    """

    id: str
    date_evaluation: datetime
    statut_global: StatutGlobalEnum
    anomalies: list[AnomalieResult]
