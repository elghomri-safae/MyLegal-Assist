"""Règles relatives à la forme juridique et à l'identité des associés.

Périmètre couvert (décision de Phase 1, PROJECT.md §5.1) : uniquement SARL
et SARL AU. Toute autre forme juridique déclenche ID-000.
"""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput

FORMES_COUVERTES = {"SARL", "SARL AU"}


def _forme_juridique_non_couverte(dossier: DossierInput) -> bool:
    return dossier.forme_juridique not in FORMES_COUVERTES


def _nombre_associes_sarl_hors_plage(dossier: DossierInput) -> bool:
    if dossier.forme_juridique != "SARL":
        return False
    nb = len(dossier.identites)
    return not (1 <= nb <= 50)


def _sarl_au_associe_unique_incorrect(dossier: DossierInput) -> bool:
    if dossier.forme_juridique != "SARL AU":
        return False
    return len(dossier.identites) != 1


def _identite_incomplete(dossier: DossierInput) -> bool:
    if dossier.forme_juridique not in FORMES_COUVERTES:
        return False
    if not dossier.identites:
        return True
    return any(not identite.numero_cin for identite in dossier.identites)


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="ID-000",
            categorie="identite",
            description=(
                "Forme juridique hors périmètre couvert par le système "
                "(SARL, SARL AU uniquement en version actuelle)."
            ),
            condition_texte="forme_juridique not in {SARL, SARL AU}",
            gravite="bloquante",
            message_utilisateur=(
                "La forme juridique renseignée n'est pas prise en charge par ce système "
                "(seules SARL et SARL AU sont couvertes en version actuelle)."
            ),
            justification=(
                "Le périmètre du système expert a été volontairement limité à la SARL et "
                "la SARL AU. Ce n'est pas une règle légale mais une contrainte de conception."
            ),
            reference_documentaire="PROJECT.md, §5 Périmètre précis (décision de Phase 0/1)",
            niveau_documentaire=0,
        ),
        est_declenchee=_forme_juridique_non_couverte,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="ID-001",
            categorie="identite",
            description="Nombre d'associés d'une SARL hors de la plage légale [1, 50].",
            condition_texte="forme_juridique == 'SARL' AND NOT (1 <= nb_associes <= 50)",
            gravite="bloquante",
            message_utilisateur=(
                "Une SARL doit compter entre 1 et 50 associés. Le nombre d'identités "
                "renseignées dans le dossier ne respecte pas cette plage."
            ),
            justification=(
                "La SARL est constituée par une ou plusieurs personnes (art. 44) et le "
                "nombre d'associés ne peut dépasser cinquante (art. 47)."
            ),
            reference_documentaire="Loi 5-96, art. 44 et art. 47",
            niveau_documentaire=1,
        ),
        est_declenchee=_nombre_associes_sarl_hors_plage,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="ID-002",
            categorie="identite",
            description="Une SARL AU doit avoir exactement un associé unique.",
            condition_texte="forme_juridique == 'SARL AU' AND nb_associes != 1",
            gravite="bloquante",
            message_utilisateur=(
                "La SARL AU (à associé unique) doit comporter exactement une identité "
                "d'associé dans le dossier. Le nombre renseigné est différent de 1."
            ),
            justification=(
                "« Lorsque la société ... ne comporte qu'une seule personne, celle-ci est "
                "dénommée associé unique. » — la SARL AU est par définition mono-associée."
            ),
            reference_documentaire="Loi 5-96, art. 44, al. 3",
            niveau_documentaire=1,
        ),
        est_declenchee=_sarl_au_associe_unique_incorrect,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="ID-003",
            categorie="identite",
            description="Pièce d'identité (CIN) manquante pour au moins un associé.",
            condition_texte="identites vide OU un associé sans numero_cin renseigné",
            gravite="bloquante",
            message_utilisateur=(
                "Chaque associé doit fournir une pièce d'identité (CIN ou passeport). "
                "Au moins une identité du dossier est incomplète ou absente."
            ),
            justification=(
                "La carte d'identité nationale (ou le passeport) est exigée pour la demande "
                "de certificat négatif et pour l'immatriculation au registre de commerce."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, FAQ certificat négatif Q1 ; "
                "Dar Al Moukawil, Guide 1, p.13 (Documents à fournir)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_identite_incomplete,
    ),
]
