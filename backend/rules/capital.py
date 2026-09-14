"""Règles relatives au capital social.

NOTE IMPORTANTE (Règle absolue n°8) : aucune règle de rejet sur un
"capital minimum" n'est implémentée (contradiction non arbitrée entre
sources — voir backend/RULES.md).
"""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput

SEUIL_BLOCAGE_CAPITAL_DH = 100_000
FORMES_COUVERTES = {"SARL", "SARL AU"}
TOLERANCE_ECART_APPORTS_DH = 0.01


def _blocage_bancaire_manquant(dossier: DossierInput) -> bool:
    if dossier.forme_juridique not in FORMES_COUVERTES:
        return False
    return (
        dossier.capital_social > SEUIL_BLOCAGE_CAPITAL_DH
        and not dossier.attestation_blocage_bancaire_fournie
    )


def _apport_en_nature_hors_perimetre(dossier: DossierInput) -> bool:
    return any(i.type_apport_personnel == "nature" for i in dossier.identites)


def _somme_apports_incoherente(dossier: DossierInput) -> bool:
    montants = [i.montant_apport for i in dossier.identites if i.montant_apport is not None]
    if not montants:
        return False
    return abs(sum(montants) - dossier.capital_social) > TOLERANCE_ECART_APPORTS_DH


def _aucun_apport_renseigne(dossier: DossierInput) -> bool:
    if dossier.capital_social <= 0:
        return False
    return all(i.montant_apport is None for i in dossier.identites)


def _message_blocage_bancaire(dossier: DossierInput) -> str:
    return (
        f"Le capital social de {dossier.capital_social:,.0f} DH dépasse le seuil de "
        f"{SEUIL_BLOCAGE_CAPITAL_DH:,.0f} DH : une attestation de blocage bancaire du "
        "capital libéré est obligatoire avant l'immatriculation."
    )


def _message_apport_nature(dossier: DossierInput) -> str:
    nb_nature = sum(1 for i in dossier.identites if i.type_apport_personnel == "nature")
    return (
        f"Ce dossier comporte un apport en nature ({nb_nature} associé(s) concerné(s)), "
        "non pris en charge par l'évaluation automatique dans cette version. Un rapport "
        "de commissaire aux apports agréé est requis pour ce type de dossier — il sera "
        "traité manuellement par un juriste MyLegal plutôt que par ce système."
    )


def _message_somme_apports(dossier: DossierInput) -> str:
    total = sum(i.montant_apport for i in dossier.identites if i.montant_apport is not None)
    return (
        f"La somme des apports déclarés par les associés ({total:,.0f} DH) ne correspond "
        f"pas au capital social renseigné ({dossier.capital_social:,.0f} DH). Vérifiez la "
        "répartition entre associés."
    )


def _message_aucun_apport(dossier: DossierInput) -> str:
    return (
        f"Aucun montant d'apport n'a été renseigné pour vos {len(dossier.identites)} "
        f"associé(s), alors que le capital social déclaré est de "
        f"{dossier.capital_social:,.0f} DH. La cohérence entre les apports individuels "
        "et le capital social ne peut pas être vérifiée tant que cette information "
        "n'est pas complétée."
    )


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="CAP-001",
            categorie="capital",
            description=(
                "Attestation de blocage bancaire du capital libéré manquante alors que le "
                "capital social dépasse 100 000 DH."
            ),
            condition_texte=(
                "capital_social > 100000 AND attestation_blocage_bancaire_fournie == False"
            ),
            gravite="bloquante",
            message_utilisateur=_message_blocage_bancaire,
            justification=(
                "La formalité de blocage bancaire est supprimée pour les sociétés dont le "
                "capital ne dépasse pas 100 000 DH ; au-delà de ce seuil, elle reste requise."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, étape 5 ; Dar Al Moukawil, Guide 1, "
                "p.10 ; Loi 5-96, art. 51, al. 3 ; Référentiel documentaire, item #8"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_blocage_bancaire_manquant,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="CAP-002",
            categorie="capital",
            description="Apport en nature : dossier hors périmètre du traitement automatisé v1.",
            condition_texte="any(identites.type_apport_personnel == 'nature')",
            gravite="bloquante",
            message_utilisateur=_message_apport_nature,
            justification=(
                "Position MyLegal : l'apport en nature est classé hors périmètre v1. Le "
                "rapport du commissaire aux apports engage une expertise externe que ce "
                "module n'a pas vocation à évaluer à ce stade."
            ),
            reference_documentaire=(
                "Référentiel documentaire création SARL/SARL AU, item #16 ; "
                "position métier MyLegal (synthèse apport en nature, hors périmètre v1)"
            ),
            niveau_documentaire=0,
        ),
        est_declenchee=_apport_en_nature_hors_perimetre,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="CAP-003",
            categorie="capital",
            description="Somme des apports déclarés par associé incohérente avec le capital social.",
            condition_texte="sum(identites.montant_apport) != capital_social",
            gravite="avertissement",
            message_utilisateur=_message_somme_apports,
            justification=(
                "Le capital social doit être exactement constitué par la somme des "
                "apports de chaque associé, en numéraire ou en nature."
            ),
            reference_documentaire="Loi 5-96, art. 50",
            niveau_documentaire=0,
        ),
        est_declenchee=_somme_apports_incoherente,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="CAP-004",
            categorie="capital",
            description="Aucun montant d'apport renseigné par les associés.",
            condition_texte="capital_social > 0 AND tous les montant_apport sont None",
            gravite="avertissement",
            message_utilisateur=_message_aucun_apport,
            justification=(
                "Le capital social doit être exactement constitué par la somme des apports "
                "de chaque associé ; sans montants renseignés, cette vérification (CAP-003) "
                "ne peut pas s'exécuter, ce qui doit être signalé plutôt que silencieux."
            ),
            reference_documentaire="Loi 5-96, art. 50",
            niveau_documentaire=0,
        ),
        est_declenchee=_aucun_apport_renseigne,
    ),
]