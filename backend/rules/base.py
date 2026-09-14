"""Structures communes utilisées par toutes les règles du système expert.

MODIFICATION (personnalisation des messages) : message_utilisateur devient
un callable (DossierInput -> str) plutôt qu'une chaîne statique. Il est
appelé une seule fois, au moment où la règle se déclenche, avec les
valeurs réelles du dossier à cet instant précis — le texte résultant est
ensuite figé dans Anomalie.message (cf. expert_service.py), cohérent avec
le principe déjà établi de ne pas re-résoudre une anomalie passée à partir
de l'état courant du dossier (pas de snapshot, mais des valeurs concrètes
gelées dans le texte dès l'origine).

``justification`` reste une chaîne statique : c'est le raisonnement légal
général (pourquoi la règle existe), indépendant du dossier précis évalué.
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
    message_utilisateur: Callable[[DossierInput], str]
    justification: str
    reference_documentaire: str
    niveau_documentaire: int

@dataclass(frozen=True)
class ExpertRule:
    """Une règle complète : métadonnées traçables + condition exécutable."""

    meta: RegleMeta
    est_declenchee: Callable[[DossierInput], bool]




    