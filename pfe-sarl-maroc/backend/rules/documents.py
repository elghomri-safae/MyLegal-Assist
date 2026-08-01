"""Règles relatives aux pièces justificatives du dossier de création."""

from __future__ import annotations

from datetime import date, timedelta

from backend.rules.base import ExpertRule, RegleMeta
from backend.schemas.dossier import DossierInput

# 3 mois ~ 90 jours. Voir la justification de DOC-001B pour la divergence
# signalée entre sources sur cette durée (Règle absolue n°8 : aucune valeur
# n'est présentée comme certaine sans réserve).
DUREE_VALIDITE_CERTIFICAT_NEGATIF_JOURS = 90


def _certificat_negatif_non_declare(dossier: DossierInput) -> bool:
    """Vrai uniquement si la case « Je confirme disposer de ce document »
    n'est pas cochée. Ne fait aucune hypothèse sur une date de délivrance :
    tant que l'utilisateur n'a pas déclaré disposer du certificat, il n'y a
    rien d'autre à vérifier (pré-vérification pédagogique, pas un contrôle
    du document lui-même).
    """
    return not dossier.certificat_negatif_fourni


def _certificat_negatif_date_depassee(dossier: DossierInput) -> bool:
    """Vrai uniquement si le certificat est déclaré disponible ET qu'une
    date de délivrance a été renseignée ET que cette date dépasse la durée
    de validité usuelle. Si aucune date n'a été renseignée, cette règle ne
    se déclenche jamais : on ne parle jamais d'expiration sur une
    information qui n'a pas été fournie (l'utilisateur a coché la case, ce
    qui suffit à considérer le document comme disponible).
    """
    if not dossier.certificat_negatif_fourni:
        return False
    if dossier.certificat_negatif_date_delivrance is None:
        return False
    limite = dossier.certificat_negatif_date_delivrance + timedelta(
        days=DUREE_VALIDITE_CERTIFICAT_NEGATIF_JOURS
    )
    return date.today() > limite


def _siege_social_manquant(dossier: DossierInput) -> bool:
    return not dossier.siege_social.strip()


def _statuts_non_fournis(dossier: DossierInput) -> bool:
    return not dossier.statuts_fournis


RULES: list[ExpertRule] = [
    ExpertRule(
        meta=RegleMeta(
            id="DOC-001",
            categorie="documents",
            description="Certificat négatif non déclaré comme disponible.",
            condition_texte="certificat_negatif_fourni == False",
            gravite="bloquante",
            message_utilisateur=(
                "Le certificat négatif n'a pas été déclaré comme disponible. "
                "Cochez la case correspondante une fois que vous l'aurez obtenu auprès "
                "de l'OMPIC."
            ),
            justification=(
                "Le certificat négatif est la première pièce nécessaire à la création "
                "d'une entreprise : il réserve le nom commercial choisi. Tant que "
                "l'utilisateur ne confirme pas en disposer, le dossier ne peut pas être "
                "considéré comme complet sur ce point."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, FAQ certificat négatif Q1 et Q3"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_certificat_negatif_non_declare,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="DOC-001B",
            categorie="documents",
            description=(
                "Certificat négatif déclaré disponible, mais la date de délivrance "
                "renseignée dépasse la durée de validité usuelle (3 mois)."
            ),
            condition_texte=(
                "certificat_negatif_fourni == True ET date_delivrance renseignée ET "
                "date_delivrance + 3 mois < date du jour"
            ),
            gravite="bloquante",
            message_utilisateur=(
                "D'après la date de délivrance que vous avez renseignée, le certificat "
                "négatif dépasse la durée de validité habituelle de 3 mois pour "
                "l'immatriculation. Ce système ne contrôle pas le document original : "
                "vérifiez sa validité réelle avant le dépôt, ou demandez-en un nouveau si "
                "nécessaire."
            ),
            justification=(
                "Le certificat négatif n'est valable que 3 mois pour finaliser "
                "l'immatriculation. Ce calcul s'appuie exclusivement sur la date de "
                "délivrance déclarée par l'utilisateur — si aucune date n'est renseignée, "
                "cette règle ne se déclenche jamais (Règle absolue n°8 : ne pas faire "
                "d'hypothèse sur une information non demandée). "
                "INFORMATION SIGNALÉE : le guide Dar Al Moukawil (index 4, p.7) mentionne "
                "un délai d'un an pour l'inscription au registre du commerce, ce qui "
                "diverge de la durée de 3 mois donnée par la FAQ officielle OMPIC et par "
                "le guide de vulgarisation (index 2). Cette règle retient la durée de "
                "3 mois (2 sources concordantes sur 3, dont la FAQ officielle OMPIC) mais "
                "la divergence doit être vérifiée auprès de l'OMPIC avant toute "
                "utilisation à valeur juridique certaine."
            ),
            reference_documentaire=(
                "OMPIC, Registre Central du Commerce, FAQ certificat négatif Q3 "
                "(« durée de validité de trois mois ») ; Documentation pratique création "
                "SARL/SARL AU, §1 (« Validité pour immatriculer : 3 mois »)"
            ),
            niveau_documentaire=2,
        ),
        est_declenchee=_certificat_negatif_date_depassee,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="DOC-002",
            categorie="documents",
            description="Justificatif de siège social manquant.",
            condition_texte="siege_social vide",
            gravite="bloquante",
            message_utilisateur=(
                "Le siège social doit être justifié (contrat de bail commercial ou contrat "
                "de domiciliation) avant la rédaction définitive des statuts."
            ),
            justification=(
                "Le siège social doit obligatoirement figurer dans les statuts et détermine "
                "le tribunal de commerce et le centre des impôts compétents."
            ),
            reference_documentaire=(
                "Loi 5-96, art. 50 (5°) ; Documentation pratique création SARL/SARL AU, §2, "
                "étape 3"
            ),
            niveau_documentaire=1,
        ),
        est_declenchee=_siege_social_manquant,
    ),
    ExpertRule(
        meta=RegleMeta(
            id="DOC-003",
            categorie="documents",
            description="Statuts non fournis ou non signés par l'ensemble des associés.",
            condition_texte="statuts_fournis == False",
            gravite="bloquante",
            message_utilisateur=(
                "Les statuts, signés par l'ensemble des associés, sont obligatoires pour "
                "constituer le dossier de création."
            ),
            justification=(
                "Tous les associés doivent intervenir à l'acte constitutif de la société, en "
                "personne ou par mandataire justifiant d'un pouvoir spécial."
            ),
            reference_documentaire="Loi 5-96, art. 50, al. 1",
            niveau_documentaire=1,
        ),
        est_declenchee=_statuts_non_fournis,
    ),
]



# """Règles relatives aux pièces justificatives du dossier de création."""

# from __future__ import annotations

# from datetime import date, timedelta

# from backend.rules.base import ExpertRule, RegleMeta
# from backend.schemas.dossier import DossierInput

# # 3 mois ~ 90 jours. Voir la justification de DOC-001 pour la divergence
# # signalée entre sources sur cette durée (Règle absolue n°8 : aucune valeur
# # n'est présentée comme certaine sans réserve).
# DUREE_VALIDITE_CERTIFICAT_NEGATIF_JOURS = 90


# def _certificat_negatif_absent_ou_expire(dossier: DossierInput) -> bool:
#     if not dossier.certificat_negatif_fourni:
#         return True
#     if dossier.certificat_negatif_date_delivrance is None:
#         return True
#     limite = dossier.certificat_negatif_date_delivrance + timedelta(
#         days=DUREE_VALIDITE_CERTIFICAT_NEGATIF_JOURS
#     )
#     return date.today() > limite


# def _siege_social_manquant(dossier: DossierInput) -> bool:
#     return not dossier.siege_social.strip()


# def _statuts_non_fournis(dossier: DossierInput) -> bool:
#     return not dossier.statuts_fournis


# RULES: list[ExpertRule] = [
#     ExpertRule(
#         meta=RegleMeta(
#             id="DOC-001",
#             categorie="documents",
#             description="Certificat négatif absent ou périmé.",
#             condition_texte=(
#                 "certificat_negatif_fourni == False OU " "date_delivrance + 3 mois < date du jour"
#             ),
#             gravite="bloquante",
#             message_utilisateur=(
#                 "Le certificat négatif est absent ou périmé. Sa durée de validité pour "
#                 "immatriculer est de 3 mois à compter de sa délivrance."
#             ),
#             justification=(
#                 "Le certificat négatif est la première pièce nécessaire à la création d'une "
#                 "entreprise et n'est valable que 3 mois pour finaliser l'immatriculation. "
#                 "INFORMATION SIGNALÉE (Règle absolue n°8) : le guide Dar Al Moukawil "
#                 "(index 4, p.7) mentionne un délai d'un an pour l'inscription au registre du "
#                 "commerce, ce qui diverge de la durée de 3 mois donnée par la FAQ officielle "
#                 "OMPIC et par le guide de vulgarisation (index 2). Cette règle retient la "
#                 "durée de 3 mois (2 sources concordantes sur 3, dont la FAQ officielle "
#                 "OMPIC) mais la divergence doit être vérifiée auprès de l'OMPIC avant toute "
#                 "utilisation à valeur juridique certaine."
#             ),
#             reference_documentaire=(
#                 "OMPIC, Registre Central du Commerce, FAQ certificat négatif Q3 "
#                 "(« durée de validité de trois mois ») ; Documentation pratique création "
#                 "SARL/SARL AU, §1 (« Validité pour immatriculer : 3 mois »)"
#             ),
#             niveau_documentaire=2,
#         ),
#         est_declenchee=_certificat_negatif_absent_ou_expire,
#     ),
#     ExpertRule(
#         meta=RegleMeta(
#             id="DOC-002",
#             categorie="documents",
#             description="Justificatif de siège social manquant.",
#             condition_texte="siege_social vide",
#             gravite="bloquante",
#             message_utilisateur=(
#                 "Le siège social doit être justifié (contrat de bail commercial ou contrat "
#                 "de domiciliation) avant la rédaction définitive des statuts."
#             ),
#             justification=(
#                 "Le siège social doit obligatoirement figurer dans les statuts et détermine "
#                 "le tribunal de commerce et le centre des impôts compétents."
#             ),
#             reference_documentaire=(
#                 "Loi 5-96, art. 50 (5°) ; Documentation pratique création SARL/SARL AU, §2, "
#                 "étape 3"
#             ),
#             niveau_documentaire=1,
#         ),
#         est_declenchee=_siege_social_manquant,
#     ),
#     ExpertRule(
#         meta=RegleMeta(
#             id="DOC-003",
#             categorie="documents",
#             description="Statuts non fournis ou non signés par l'ensemble des associés.",
#             condition_texte="statuts_fournis == False",
#             gravite="bloquante",
#             message_utilisateur=(
#                 "Les statuts, signés par l'ensemble des associés, sont obligatoires pour "
#                 "constituer le dossier de création."
#             ),
#             justification=(
#                 "Tous les associés doivent intervenir à l'acte constitutif de la société, en "
#                 "personne ou par mandataire justifiant d'un pouvoir spécial."
#             ),
#             reference_documentaire="Loi 5-96, art. 50, al. 1",
#             niveau_documentaire=1,
#         ),
#         est_declenchee=_statuts_non_fournis,
#     ),
# ]
