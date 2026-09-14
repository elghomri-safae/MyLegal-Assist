"""Service d'évaluation d'un dossier par le système expert anti-rejet.

Le statut global est déduit de la gravité maximale rencontrée parmi les
anomalies déclenchées : une anomalie "bloquante" rend le dossier
non-conforme ; en l'absence de bloquante, une "avertissement" donne un
statut "conforme avec réserves" ; les anomalies "informative" n'affectent
jamais le statut global (elles ne sont que des rappels documentaires, par
exemple FISC-002).
"""

from __future__ import annotations

import uuid

from backend.models.enums import StatutGlobalEnum
from backend.rules import ALL_RULES
from backend.schemas.dossier import DossierInput
from backend.schemas.evaluation import AnomalieResult, VerdictDossier


def evaluer_dossier(dossier: DossierInput) -> VerdictDossier:
    """Évalue un dossier via l'ensemble des règles du système expert."""
    anomalies: list[AnomalieResult] = []

    for regle in ALL_RULES:
        if regle.est_declenchee(dossier):
            anomalies.append(
                AnomalieResult(
                    id=str(uuid.uuid4()),
                    regle_id=regle.meta.id,
                    categorie=regle.meta.categorie,
                    gravite=regle.meta.gravite,
                    # Résolu ici, une seule fois, avec les valeurs réelles
                    # du dossier au moment de l'évaluation — le texte
                    # obtenu est ensuite figé dans Anomalie.message.
                    message=regle.meta.message_utilisateur(dossier),
                    justification=regle.meta.justification,
                    reference_documentaire=regle.meta.reference_documentaire,
                    niveau_documentaire=regle.meta.niveau_documentaire,
                )
            )

    return VerdictDossier(statut_global=_statut_global(anomalies), anomalies=anomalies)


def _statut_global(anomalies: list[AnomalieResult]) -> StatutGlobalEnum:
    """Déduit le verdict global à partir de la gravité maximale rencontrée."""
    if any(a.gravite == "bloquante" for a in anomalies):
        return StatutGlobalEnum.NON_CONFORME
    if any(a.gravite == "avertissement" for a in anomalies):
        return StatutGlobalEnum.CONFORME_AVEC_RESERVES
    return StatutGlobalEnum.CONFORME



