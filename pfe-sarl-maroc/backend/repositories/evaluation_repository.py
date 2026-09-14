"""Accès aux données pour la persistance des évaluations (CONCEPTION_V2.md §4.3, §9.4)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.evaluation import Anomalie, Evaluation
from backend.schemas.evaluation import VerdictDossier


class EvaluationRepository:
    """Repository SQLAlchemy pour les évaluations d'un dossier et leurs anomalies."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def creer(self, dossier_id: uuid.UUID, verdict: VerdictDossier) -> Evaluation:
        """Persiste une évaluation et ses anomalies, sans snapshot du dossier
        (CONCEPTION_V2.md §4.3) : chaque anomalie porte déjà tout le contexte
        nécessaire (règle, gravité, message, justification, référence).
        """
        evaluation = Evaluation(dossier_id=dossier_id, statut_global=verdict.statut_global)
        for anomalie in verdict.anomalies:
            evaluation.anomalies.append(
                Anomalie(
                    regle_id=anomalie.regle_id,
                    categorie=anomalie.categorie,
                    message=anomalie.message,
                    gravite=anomalie.gravite,
                    justification=anomalie.justification,
                    reference_documentaire=anomalie.reference_documentaire,
                    niveau_documentaire=anomalie.niveau_documentaire,
                )
            )
        self._db.add(evaluation)
        self._db.commit()
        self._db.refresh(evaluation)
        return evaluation

    def lister_pour_dossier(self, dossier_id: uuid.UUID) -> list[Evaluation]:
        """Historique complet, du plus récent au plus ancien (CONCEPTION_V2.md §9.4)."""
        stmt = (
            select(Evaluation)
            .where(Evaluation.dossier_id == dossier_id)
            .options(selectinload(Evaluation.anomalies))
            .order_by(Evaluation.date_evaluation.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def derniere_pour_dossier(self, dossier_id: uuid.UUID) -> Evaluation | None:
        stmt = (
            select(Evaluation)
            .where(Evaluation.dossier_id == dossier_id)
            .options(selectinload(Evaluation.anomalies))
            .order_by(Evaluation.date_evaluation.desc())
            .limit(1)
        )
        return self._db.execute(stmt).scalar_one_or_none()
