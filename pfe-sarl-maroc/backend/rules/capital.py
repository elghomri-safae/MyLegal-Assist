"""Règles relatives au capital social.

NOTE IMPORTANTE (Règle absolue n°8) : le corpus fourni ne permet PAS
d'affirmer un montant de capital minimum sans ambiguïté pour la SARL. Le
texte de la Loi 5-96 fourni (art. 46) indique un minimum de 100 000 DH,
mais trois autres sources (OMPIC, Dar Al Moukawil, guide de vulgarisation)
indiquent explicitement l'absence de minimum ("capital libre depuis la
réforme de 2006"). Cette contradiction n'est pas arbitrée ici : AUCUNE
règle de rejet sur un "capital minimum" n'est implémentée. Voir
backend/RULES.md pour le détail de cette divergence.

Seule la règle du blocage bancaire au-delà de 100 000 DH est implémentée,
car elle est concordante entre toutes les sources disponibles.
"""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput

SEUIL_BLOCAGE_CAPITAL_DH = 100_000
FORMES_COUVERTES = {"SARL", "SARL AU"}


def _blocage_bancaire_manquant(dossier: DossierInput) -> bool:
    if dossier.forme_juridique not in FORMES_COUVERTES:
        return False
    return (
        dossier.capital_social > SEUIL_BLOCAGE_CAPITAL_DH
        and not dossier.attestation_blocage_bancaire_fournie
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
            message_utilisateur=(
                "Le capital social dépasse 100 000 DH : une attestation de blocage bancaire "
                "du capital libéré est obligatoire avant l'immatriculation."
            ),
            justification=(
                "La formalité de blocage bancaire est supprimée pour les sociétés dont le "
                "capital ne dépasse pas 100 000 DH ; au-delà de ce seuil, elle reste requise "
                "(dépôt des fonds sur un compte bancaire bloqué, attestation délivrée par la "
                "banque)."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, étape 5 (Blocage du montant du capital "
                "libéré) ; Dar Al Moukawil, Guide 1, p.10 ; Loi 5-96, art. 51, al. 3 "
                "(obligation générale de dépôt en compte bancaire bloqué)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_blocage_bancaire_manquant,
    ),
]
