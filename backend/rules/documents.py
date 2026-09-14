"""Règles relatives aux pièces justificatives du dossier de création.

Le certificat négatif est intégralement pris en charge par MyLegal (voir
nettoyage précédent) : DOC-001 est un rappel systématique.
"""

from __future__ import annotations

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput

FORMES_COUVERTES = {"SARL", "SARL AU"}


def _certificat_negatif_non_declare(dossier: DossierInput) -> bool:
    return dossier.forme_juridique in FORMES_COUVERTES


def _siege_social_manquant(dossier: DossierInput) -> bool:
    return not dossier.siege_social.strip()


def _type_justificatif_siege_non_selectionne(dossier: DossierInput) -> bool:
    return not dossier.type_justificatif_siege


def _pv_nomination_gerant_requis(dossier: DossierInput) -> bool:
    return not dossier.gerant_designe_dans_statuts


def _statuts_non_fournis(dossier: DossierInput) -> bool:
    return not dossier.statuts_fournis


def _message_certificat_negatif(dossier: DossierInput) -> str:
    return (
        f"Pour votre dossier « {dossier.forme_juridique} », le certificat négatif sera "
        "obtenu par MyLegal auprès de l'OMPIC sur la base du nom que vous aurez choisi — "
        "ce n'est pas une pièce que vous devez obtenir vous-même. Ceci est un rappel, pas "
        "un point bloquant de votre côté."
    )


def _message_siege_manquant(_dossier: DossierInput) -> str:
    return (
        "Le siège social doit être justifié (contrat de bail commercial ou contrat "
        "de domiciliation) avant la rédaction définitive des statuts."
    )


def _message_type_justificatif_siege(_dossier: DossierInput) -> str:
    return (
        "Précisez le type de justificatif de siège social pour votre dossier : "
        "contrat de bail signé et enregistré, attestation de domiciliation, ou "
        "certificat de propriété. Ce justificatif est obligatoire dans tous les cas."
    )


def _message_pv_nomination_gerant(dossier: DossierInput) -> str:
    nb_associes = len(dossier.identites)
    return (
        "Le gérant n'est pas désigné directement dans vos statuts : un procès-verbal "
        "de nomination séparé est donc nécessaire. MyLegal se charge de le rédiger à "
        f"partir des informations de vos {nb_associes} associé(s) — ce n'est pas un "
        "document que vous devez rédiger ou obtenir vous-même."
    )


def _message_statuts_non_fournis(_dossier: DossierInput) -> str:
    return (
        "Les statuts, signés par l'ensemble des associés, sont obligatoires pour "
        "constituer le dossier de création."
    )


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="DOC-001",
            categorie="documents",
            description="Rappel informatif : certificat négatif obtenu par MyLegal.",
            condition_texte="toujours déclenchée pour SARL/SARL AU (rappel systématique)",
            gravite="informative",
            message_utilisateur=_message_certificat_negatif,
            justification=(
                "Le référentiel documentaire (item #2) classe ce document comme obtenu par "
                "le cabinet sur mandat auprès de l'OMPIC — jamais fourni directement par le "
                "client (référentiel, §2.4)."
            ),
            reference_documentaire=(
                "Référentiel documentaire création SARL/SARL AU, item #2 et §2.4 ; "
                "OMPIC, liste des pièces CN"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_certificat_negatif_non_declare,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="DOC-002",
            categorie="documents",
            description="Justificatif de siège social manquant.",
            condition_texte="siege_social vide",
            gravite="bloquante",
            message_utilisateur=_message_siege_manquant,
            justification=(
                "Le siège social doit obligatoirement figurer dans les statuts et détermine "
                "le tribunal de commerce et le centre des impôts compétents."
            ),
            reference_documentaire=(
                "Loi 5-96, art. 50 (5°) ; Référentiel documentaire création SARL/SARL AU, "
                "item #7 (🟢, obligatoire)"
            ),
            niveau_documentaire=1,
        ),
        est_declenchee=_siege_social_manquant,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="DOC-002B",
            categorie="documents",
            description="Type de justificatif de siège non sélectionné (toujours obligatoire).",
            condition_texte="type_justificatif_siege vide",
            gravite="bloquante",
            message_utilisateur=_message_type_justificatif_siege,
            justification=(
                "Le justificatif de siège social est une pièce obligatoire du dossier CRI, "
                "quel que soit son type."
            ),
            reference_documentaire=(
                "Référentiel documentaire création SARL/SARL AU, item #7 ; "
                "position métier MyLegal (synthèse justificatif de siège)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_type_justificatif_siege_non_selectionne,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="DOC-004",
            categorie="documents",
            description="Rappel informatif : PV de nomination du gérant requis.",
            condition_texte="gerant_designe_dans_statuts == False",
            gravite="informative",
            message_utilisateur=_message_pv_nomination_gerant,
            justification=(
                "Position MyLegal : le PV de nomination n'est exigé que si le gérant n'est "
                "pas déjà désigné dans le corps des statuts."
            ),
            reference_documentaire=(
                "Référentiel documentaire création SARL/SARL AU, item #6 ; "
                "position métier MyLegal (synthèse PV de nomination du gérant)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_pv_nomination_gerant_requis,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="DOC-003",
            categorie="documents",
            description="Statuts non fournis ou non signés par l'ensemble des associés.",
            condition_texte="statuts_fournis == False",
            gravite="bloquante",
            message_utilisateur=_message_statuts_non_fournis,
            justification=(
                "Tous les associés doivent intervenir à l'acte constitutif de la société."
            ),
            reference_documentaire=(
                "Loi 5-96, art. 50, al. 1 ; Référentiel documentaire création SARL/SARL AU, "
                "item #5"
            ),
            niveau_documentaire=1,
        ),
        est_declenchee=_statuts_non_fournis,
    ),
]