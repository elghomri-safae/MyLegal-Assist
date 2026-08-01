"""Règles relatives à l'affiliation CNSS.

L'affiliation CNSS intervient généralement après l'immatriculation (étape 9
du parcours OMPIC, après l'étape 8 « Immatriculation »). Elle est donc
modélisée comme un avertissement (obligation légale à venir) et non comme
une cause de rejet de l'immatriculation elle-même.
"""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput


def _salaries_sans_affiliation_cnss(dossier: DossierInput) -> bool:
    return dossier.emploie_salaries and not dossier.affiliation_cnss_fournie


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="CNSS-001",
            categorie="cnss",
            description="Société employant des salariés sans affiliation CNSS renseignée.",
            condition_texte="emploie_salaries == True AND affiliation_cnss_fournie == False",
            gravite="avertissement",
            message_utilisateur=(
                "La société déclare employer des salariés : l'affiliation à la CNSS est une "
                "obligation légale et doit être effectuée (numéro d'affiliation délivré par "
                "la CNSS)."
            ),
            justification=(
                "Toute entreprise assujettie au régime de sécurité sociale doit être "
                "affiliée à la CNSS, qui lui délivre un numéro d'affiliation valant "
                "reconnaissance administrative."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, étape 9 (Affiliation à la CNSS) ; "
                "Dar Al Moukawil, Guide 1, p.14"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_salaries_sans_affiliation_cnss,
    ),
]
