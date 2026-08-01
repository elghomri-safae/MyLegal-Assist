"""Règles fiscales liées à la création d'entreprise."""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput

FORMES_COUVERTES = {"SARL", "SARL AU"}


def _taxe_professionnelle_non_declaree(dossier: DossierInput) -> bool:
    if dossier.forme_juridique not in FORMES_COUVERTES:
        return False
    return not dossier.taxe_professionnelle_declaree


def _rappel_droit_enregistrement(_dossier: DossierInput) -> bool:
    """Rappel systématique (gravité informative) — voir justification de FISC-002."""
    return True


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="FISC-001",
            categorie="fiscalite",
            description="Déclaration d'inscription à la taxe professionnelle manquante.",
            condition_texte="taxe_professionnelle_declaree == False",
            gravite="bloquante",
            message_utilisateur=(
                "La déclaration d'inscription à la taxe professionnelle est requise parmi "
                "les documents à présenter pour l'immatriculation au registre de commerce."
            ),
            justification=(
                "La société doit préparer une demande d'immatriculation accompagnée de la "
                "déclaration de la taxe professionnelle, du certificat négatif et des "
                "statuts."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, étape 8 (Immatriculation au registre "
                "de commerce, « Documents à présenter »)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_taxe_professionnelle_non_declaree,
    ),
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
            message_utilisateur=(
                "Le droit d'enregistrement des statuts est dû. Le corpus documentaire "
                "fournit deux formulations non totalement concordantes : (a) 1 % du capital "
                "avec un minimum de 1000 DH (OMPIC) ; (b) droit fixe de 1000 DH si le capital "
                "ne dépasse pas 500 000 DH, sinon 1 % du capital (Dar Al Moukawil). Ce montant "
                "doit être confirmé auprès de la Direction Régionale des Impôts avant "
                "paiement."
            ),
            justification=(
                "Divergence signalée entre deux sources de niveau 2 sur la formule exacte du "
                "droit d'enregistrement ; aucune valeur unique n'est donc affirmée comme "
                "certaine par le système (Règle absolue n°8)."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, étape 6 (Enregistrement des actes) ; "
                "Dar Al Moukawil, Guide 1, p.11 (Frais d'enregistrement)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_rappel_droit_enregistrement,
    ),
]
