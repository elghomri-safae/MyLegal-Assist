"""Règles relatives à l'affiliation CNSS."""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput


def _salaries_sans_affiliation_cnss(dossier: DossierInput) -> bool:
    return dossier.emploie_salaries


def _message_affiliation_cnss(_dossier: DossierInput) -> str:
    return (
        "Votre société déclare employer des salariés : l'affiliation à la CNSS est "
        "une obligation légale. MyLegal peut préparer et déposer cette demande sur "
        "votre mandat — ce n'est pas une pièce que vous devez obtenir vous-même. "
        "Ceci est un rappel, pas un point bloquant de votre côté."
    )


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="CNSS-001",
            categorie="cnss",
            description="Rappel informatif : société employant des salariés.",
            condition_texte="emploie_salaries == True",
            gravite="informative",
            message_utilisateur=_message_affiliation_cnss,
            justification=(
                "Toute entreprise assujettie au régime de sécurité sociale doit être "
                "affiliée à la CNSS."
            ),
            reference_documentaire=(
                "Référentiel documentaire création SARL/SARL AU, item #13 ; "
                "OMPIC, Registre Central du Commerce, étape 9 ; CNSS, page Affiliation"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_salaries_sans_affiliation_cnss,
    ),
]