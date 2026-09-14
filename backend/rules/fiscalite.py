"""Règles fiscales liées à la création d'entreprise."""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput


def _rappel_droit_enregistrement(_dossier: DossierInput) -> bool:
    return True


def _message_droit_enregistrement(dossier: DossierInput) -> str:
    minimum = max(1000, round(dossier.capital_social * 0.01))
    return (
        "Le droit d'enregistrement des statuts est dû. Le corpus documentaire fournit "
        "deux formulations non totalement concordantes : (a) 1 % du capital avec un "
        "minimum de 1000 DH (OMPIC) ; (b) droit fixe de 1000 DH si le capital ne dépasse "
        "pas 500 000 DH, sinon 1 % du capital (Dar Al Moukawil). Pour votre capital "
        f"déclaré ({dossier.capital_social:,.0f} DH), le montant serait de l'ordre de "
        f"{minimum:,.0f} DH selon la première formule — à confirmer auprès de la "
        "Direction Régionale des Impôts avant paiement."
    )


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="FISC-002",
            categorie="fiscalite",
            description=(
                "Rappel informatif : montant du droit d'enregistrement des statuts "
                "(formule partiellement contradictoire dans le corpus, à vérifier)."
            ),
            condition_texte="toujours déclenchée (rappel systématique, gravité informative)",
            gravite="informative",
            message_utilisateur=_message_droit_enregistrement,
            justification=(
                "Divergence signalée entre deux sources de niveau 2 sur la formule exacte du "
                "droit d'enregistrement ; aucune valeur unique n'est donc affirmée comme "
                "certaine par le système (Règle absolue n°8)."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, étape 6 ; Dar Al Moukawil, Guide 1, "
                "p.11 (Frais d'enregistrement)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_rappel_droit_enregistrement,
    ),
]