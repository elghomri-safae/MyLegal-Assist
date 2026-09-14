"""Structures communes utilisées par toutes les règles du système expert.

La structure ``RegleMeta`` reprend exactement les champs imposés par le
cahier des charges : identifiant, catégorie, description, condition,
gravité, message utilisateur, justification, référence documentaire,
niveau documentaire. ``ExpertRule`` associe ces métadonnées tracables à la
fonction Python qui évalue réellement la condition sur un dossier donné.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from backend.schemas.dossier import DossierInput


@dataclass(frozen=True)
class RegleMeta:
    """Métadonnées déclaratives et traçables d'une règle du système expert."""

    id: str
    categorie: str
    description: str
    condition_texte: str
    gravite: str
    message_utilisateur: str
    justification: str
    reference_documentaire: str
    niveau_documentaire: int


ConditionFn = Callable[[DossierInput], bool]


@dataclass(frozen=True)
class ExpertRule:
    """Une règle complète : métadonnées traçables + condition exécutable."""

    meta: RegleMeta
    est_declenchee: ConditionFn
