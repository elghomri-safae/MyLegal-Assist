"""Page Streamlit du dossier persistant (CONCEPTION_V2.md §2, §5, §8, §9).

Module d'évaluation stabilisé : chaque pièce demandée est présentée comme
une carte d'information pédagogique (pourquoi, où l'obtenir, validité,
conseils, erreurs fréquentes) plutôt qu'une simple case à cocher isolée.
Le rapport final utilise des libellés sobres et colorés (Conforme /
Attention / Non conforme), sans emoji, adapté à une plateforme juridique
professionnelle.

Cette page est un outil de préparation destiné aux entrepreneurs avant le
dépôt du dossier chez MyLegal. Le système ne vérifie pas les documents
originaux : il évalue uniquement les informations déclarées par
l'utilisateur (voir la note explicative affichée avant chaque évaluation).
"""

import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# --- Catalogue des pièces du dossier, sous forme de cartes d'information ---
# Chaque entrée correspond à un champ booléen "je confirme disposer de ce
# document" du dossier persisté. Le contenu pédagogique (pourquoi, où
# l'obtenir, conseils, erreurs fréquentes) reprend les éléments déjà établis
# dans les justifications des règles du système expert (backend/RULES.md),
# pour rester cohérent avec le corpus documentaire du projet.
DOCUMENTS = [
    {
        "cle": "statuts_fournis",
        "nom": "Statuts de la société",
        "pourquoi": (
            "Les statuts constituent l'acte fondateur de la société : ils fixent les "
            "règles de fonctionnement et doivent être signés par l'ensemble des associés."
        ),
        "ou_obtenir": (
            "Rédigés par un professionnel (notaire, avocat, fiduciaire) ou par le porteur "
            "de projet, puis signés par tous les associés."
        ),
        "validite": "Aucune durée de validité.",
        "conseil": "Vérifiez que chaque associé a bien signé avant le dépôt du dossier.",
        "erreurs_frequentes": "Signature manquante de l'un des associés.",
        "libelle_checkbox": "Je confirme disposer des statuts signés par l'ensemble des associés.",
    },
    {
        "cle": "certificat_negatif_fourni",
        "nom": "Certificat négatif",
        "pourquoi": "Réserver le nom commercial choisi pour la société.",
        "ou_obtenir": "OMPIC (Office Marocain de la Propriété Industrielle et Commerciale).",
        "validite": (
            "3 mois à compter de la délivrance pour finaliser l'immatriculation, selon la "
            "majorité des sources du corpus documentaire (une source mentionne un délai "
            "d'un an — divergence signalée, à vérifier auprès de l'OMPIC)."
        ),
        "conseil": "Ne pas attendre l'approche de l'expiration avant de déposer le dossier.",
        "erreurs_frequentes": "Certificat périmé au moment du dépôt effectif.",
        "libelle_checkbox": "Je confirme disposer d'un certificat négatif.",
        "champ_date": "certificat_negatif_date_delivrance",
        "libelle_date": "Date de délivrance (facultatif)",
    },
    {
        "cle": "attestation_blocage_bancaire_fournie",
        "nom": "Attestation de blocage bancaire du capital",
        "pourquoi": (
            "Justifie le dépôt des fonds du capital libéré sur un compte bancaire bloqué, "
            "obligatoire lorsque le capital social dépasse 100 000 DH."
        ),
        "ou_obtenir": "Banque où le compte de dépôt du capital a été ouvert.",
        "validite": "Aucune durée de validité.",
        "conseil": "Uniquement nécessaire si le capital social dépasse 100 000 DH.",
        "erreurs_frequentes": "Attestation manquante malgré un capital social élevé.",
        "libelle_checkbox": "Je confirme disposer de cette attestation (si applicable).",
    },
    {
        "cle": "taxe_professionnelle_declaree",
        "nom": "Déclaration d'inscription à la taxe professionnelle",
        "pourquoi": (
            "Requise parmi les documents à présenter pour l'immatriculation au registre de "
            "commerce."
        ),
        "ou_obtenir": "Direction Régionale des Impôts.",
        "validite": "Aucune durée de validité.",
        "conseil": "À préparer en parallèle du reste du dossier d'immatriculation.",
        "erreurs_frequentes": "Déclaration non préparée avant le dépôt du dossier complet.",
        "libelle_checkbox": "Je confirme disposer de cette déclaration.",
    },
    {
        "cle": "affiliation_cnss_fournie",
        "nom": "Affiliation CNSS",
        "pourquoi": "Obligation légale pour toute entreprise employant des salariés.",
        "ou_obtenir": "CNSS (Caisse Nationale de Sécurité Sociale).",
        "validite": "Aucune durée de validité.",
        "conseil": (
            "Intervient généralement après l'immatriculation. À anticiper si vous prévoyez "
            "d'employer des salariés dès le démarrage de l'activité."
        ),
        "erreurs_frequentes": "Affiliation oubliée après le recrutement des premiers salariés.",
        "libelle_checkbox": "Je confirme disposer du numéro d'affiliation CNSS (si applicable).",
    },
]

CARTE_IDENTITE = {
    "nom": "Pièce d'identité de chaque associé (CIN ou passeport)",
    "pourquoi": (
        "Exigée pour la demande de certificat négatif et pour l'immatriculation au registre "
        "de commerce."
    ),
    "ou_obtenir": "Déjà en possession de chaque associé (carte d'identité nationale ou passeport).",
    "validite": "Selon la date de validité de la pièce elle-même — non contrôlée par ce système.",
    "conseil": "Vérifiez que le numéro de CIN saisi est complet et correspond à la pièce réelle.",
    "erreurs_frequentes": "Numéro de CIN manquant ou mal renseigné pour un ou plusieurs associés.",
}

CARTE_SIEGE_SOCIAL = {
    "nom": "Justificatif de siège social",
    "pourquoi": (
        "Le siège social doit obligatoirement figurer dans les statuts et détermine le "
        "tribunal de commerce et le centre des impôts compétents."
    ),
    "ou_obtenir": "Contrat de bail commercial ou contrat de domiciliation.",
    "validite": "Selon la durée du contrat de bail ou de domiciliation.",
    "conseil": "Vérifiez que l'adresse saisie ici correspond exactement à celle du justificatif.",
    "erreurs_frequentes": "Adresse renseignée incohérente avec le justificatif réel.",
}

NOTE_EVALUATION = (
    "Cette évaluation est une pré-vérification pédagogique, basée uniquement sur les "
    "informations que vous déclarez ci-dessous. Elle ne contrôle pas les documents "
    "originaux : ceux-ci seront vérifiés ultérieurement par les juristes de MyLegal, avant "
    "le dépôt officiel du dossier."
)

_LIBELLES_VERDICT = {
    "conforme": ("Conforme", "green"),
    "conforme_avec_reserves": ("Attention", "orange"),
    "non_conforme": ("Non conforme", "red"),
}
_LIBELLES_GRAVITE = {
    "bloquante": ("Non conforme", "red"),
    "avertissement": ("Attention", "orange"),
    "informative": ("Information", "blue"),
}


def _badge(libelle: str, couleur: str) -> str:
    """Libellé coloré sobre (pas d'emoji) — CONCEPTION_V2.md, phase de
    stabilisation du module Évaluation."""
    return f":{couleur}[**{libelle}**]"


st.set_page_config(page_title="Dossiers de création", layout="wide")
st.title("Mes dossiers de création de SARL / SARL AU")

if not st.session_state.get("jeton_acces"):
    st.warning("Veuillez vous connecter depuis la page d'accueil pour accéder à vos dossiers.")
    st.stop()

en_tete = {"Authorization": f"Bearer {st.session_state.jeton_acces}"}


def _appel(methode, chemin, **kwargs):
    try:
        reponse = requests.request(
            methode, f"{API_BASE_URL}{chemin}", headers=en_tete, timeout=30, **kwargs
        )
        reponse.raise_for_status()
        return reponse.json(), None
    except requests.RequestException as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", "") if exc.response is not None else ""
        except Exception:  # noqa: BLE001 - affichage best-effort de l'erreur API
            detail = ""
        return None, detail or str(exc)


# --- Tableau de bord (CONCEPTION_V2.md §9.1) --------------------------------
st.subheader("Tableau de bord")
dossiers, erreur = _appel("GET", "/dossiers")
if erreur:
    st.error(f"Impossible de charger vos dossiers : {erreur}")
    dossiers = []

if dossiers:
    for d in dossiers:
        with st.container(border=True):
            colonnes = st.columns([3, 2, 2, 2, 2])
            colonnes[0].markdown(f"**{d['nom_projet']}** ({d['forme_juridique']})")
            colonnes[1].markdown(f"Statut : {_badge(d['statut'], 'gray')}")
            colonnes[2].markdown(f"Erreurs bloquantes : **{d['nb_erreurs_bloquantes']}**")
            colonnes[3].markdown(f"Avertissements : **{d['nb_avertissements']}**")
            colonnes[4].markdown(f"Progression : **{d['progression_pct']}%**")
            if d["pret_pour_depot"]:
                st.markdown(_badge("Prêt pour dépôt", "green"))
            if d["date_derniere_evaluation"]:
                st.caption(f"Dernière évaluation : {d['date_derniere_evaluation']}")
else:
    st.info("Aucun dossier pour l'instant. Créez-en un ci-dessous.")

st.divider()

# --- Création d'un nouveau dossier ------------------------------------------
st.subheader("Créer un nouveau dossier")
with st.form("formulaire_creation_dossier"):
    nom_projet = st.text_input("Nom du projet")
    forme_juridique = st.selectbox("Forme juridique", ["SARL", "SARL AU"])
    capital_social = st.number_input("Capital social (DH)", min_value=1.0, step=1000.0)
    siege_social = st.text_input("Siège social")
    valide_creation = st.form_submit_button("Créer le dossier")

if valide_creation:
    payload = {
        "nom_projet": nom_projet,
        "forme_juridique": forme_juridique,
        "capital_social": capital_social,
        "siege_social": siege_social,
    }
    resultat, erreur = _appel("POST", "/dossiers", json=payload)
    if erreur:
        st.error(f"Création refusée : {erreur}")
    else:
        st.success(f"Dossier « {resultat['nom_projet']} » créé.")
        st.rerun()

st.divider()

# --- Remplissage progressif, identités, évaluation ---------------------------
st.subheader("Compléter et évaluer un dossier")

if not dossiers:
    st.stop()

options = {d["nom_projet"]: d["id"] for d in dossiers}
choix_nom = st.selectbox("Dossier à compléter", list(options.keys()))
dossier_id = options[choix_nom]
dossier_courant = next(d for d in dossiers if d["id"] == dossier_id)

st.info(NOTE_EVALUATION)

# --- Siège social ------------------------------------------------------------
with st.container(border=True):
    st.markdown(f"#### {CARTE_SIEGE_SOCIAL['nom']}")
    colonne_info, colonne_action = st.columns([2, 1])
    with colonne_info:
        st.markdown(f"**Pourquoi ?** {CARTE_SIEGE_SOCIAL['pourquoi']}")
        st.markdown(f"**Où l'obtenir ?** {CARTE_SIEGE_SOCIAL['ou_obtenir']}")
        st.markdown(f"**Validité** {CARTE_SIEGE_SOCIAL['validite']}")
        st.markdown(f"**Conseil** {CARTE_SIEGE_SOCIAL['conseil']}")
        st.markdown(f"**Erreur fréquente** {CARTE_SIEGE_SOCIAL['erreurs_frequentes']}")
    with colonne_action:
        siege_social_saisi = st.text_input(
            "Adresse du siège social", value=dossier_courant["siege_social"], key="siege_social_input"
        )

# --- Cartes documents (case à cocher "je confirme disposer") ----------------
valeurs_documents: dict[str, bool] = {}
valeurs_dates: dict[str, object] = {}

for document in DOCUMENTS:
    with st.container(border=True):
        st.markdown(f"#### {document['nom']}")
        colonne_info, colonne_action = st.columns([2, 1])
        with colonne_info:
            st.markdown(f"**Pourquoi ?** {document['pourquoi']}")
            st.markdown(f"**Où l'obtenir ?** {document['ou_obtenir']}")
            st.markdown(f"**Validité** {document['validite']}")
            st.markdown(f"**Conseil** {document['conseil']}")
            st.markdown(f"**Erreur fréquente** {document['erreurs_frequentes']}")
        with colonne_action:
            valeurs_documents[document["cle"]] = st.checkbox(
                document["libelle_checkbox"],
                value=dossier_courant[document["cle"]],
                key=f"checkbox_{document['cle']}",
            )
            if "champ_date" in document:
                valeur_actuelle = dossier_courant.get(document["champ_date"])
                valeurs_dates[document["champ_date"]] = st.date_input(
                    document["libelle_date"],
                    value=None,
                    key=f"date_{document['champ_date']}",
                    help=(
                        f"Actuellement enregistrée : {valeur_actuelle}"
                        if valeur_actuelle
                        else "Aucune date enregistrée pour l'instant."
                    ),
                )

emploie_salaries_saisi = st.checkbox(
    "L'entreprise emploiera des salariés", value=dossier_courant["emploie_salaries"]
)

if st.button("Enregistrer les informations du dossier"):
    payload = {
        "siege_social": siege_social_saisi,
        "emploie_salaries": emploie_salaries_saisi,
        **valeurs_documents,
    }
    for champ, valeur in valeurs_dates.items():
        if valeur is not None:
            payload[champ] = str(valeur)
    _, erreur = _appel("PATCH", f"/dossiers/{dossier_id}", json=payload)
    if erreur:
        st.error(f"Mise à jour refusée : {erreur}")
    else:
        st.success("Dossier mis à jour.")
        st.rerun()

st.divider()

# --- Associés (identités) -----------------------------------------------------
st.subheader("Associés")
with st.container(border=True):
    st.markdown(f"#### {CARTE_IDENTITE['nom']}")
    st.markdown(f"**Pourquoi ?** {CARTE_IDENTITE['pourquoi']}")
    st.markdown(f"**Où l'obtenir ?** {CARTE_IDENTITE['ou_obtenir']}")
    st.markdown(f"**Validité** {CARTE_IDENTITE['validite']}")
    st.markdown(f"**Conseil** {CARTE_IDENTITE['conseil']}")
    st.markdown(f"**Erreur fréquente** {CARTE_IDENTITE['erreurs_frequentes']}")

with st.form("formulaire_identite"):
    colonnes = st.columns(4)
    nom = colonnes[0].text_input("Nom")
    prenom = colonnes[1].text_input("Prénom")
    numero_cin = colonnes[2].text_input("Numéro CIN")
    date_naissance = colonnes[3].date_input("Date de naissance", value=None)
    valide_identite = st.form_submit_button("Ajouter cet associé")

if valide_identite:
    payload = {
        "nom": nom,
        "prenom": prenom,
        "numero_cin": numero_cin,
        "date_naissance": str(date_naissance) if date_naissance else None,
    }
    _, erreur = _appel("POST", f"/dossiers/{dossier_id}/identites", json=payload)
    if erreur:
        st.error(f"Ajout refusé : {erreur}")
    else:
        st.success("Associé ajouté.")
        st.rerun()

st.divider()

# --- Évaluation et rapport ----------------------------------------------------
st.subheader("Évaluation du dossier")
st.info(NOTE_EVALUATION)

if st.button("Lancer une évaluation", type="primary"):
    resultat, erreur = _appel("POST", f"/dossiers/{dossier_id}/evaluer")
    if erreur:
        st.error(f"Évaluation impossible : {erreur}")
    else:
        libelle, couleur = _LIBELLES_VERDICT.get(resultat["statut_global"], (resultat["statut_global"], "gray"))
        st.markdown(f"### Résultat : {_badge(libelle, couleur)}")

        if not resultat["anomalies"]:
            st.markdown(_badge("Conforme", "green") + " — aucune anomalie détectée.")
        for anomalie in resultat["anomalies"]:
            libelle_gravite, couleur_gravite = _LIBELLES_GRAVITE.get(
                anomalie["gravite"], (anomalie["gravite"], "gray")
            )
            with st.container(border=True):
                st.markdown(f"**{anomalie['message']}** — {_badge(libelle_gravite, couleur_gravite)}")
                st.markdown(f"**Justification juridique** {anomalie['justification']}")
                st.caption(
                    f"Source : {anomalie['reference_documentaire']} "
                    f"(niveau {anomalie['niveau_documentaire']})"
                )

st.divider()

# --- Historique des évaluations ----------------------------------------------
st.subheader("Historique des évaluations")
historique, erreur = _appel("GET", f"/dossiers/{dossier_id}/evaluations")
if erreur:
    st.error(f"Historique indisponible : {erreur}")
elif not historique:
    st.info("Aucune évaluation pour l'instant.")
else:
    for evaluation in historique:
        libelle, couleur = _LIBELLES_VERDICT.get(
            evaluation["statut_global"], (evaluation["statut_global"], "gray")
        )
        with st.expander(f"{evaluation['date_evaluation']} — {libelle}"):
            if not evaluation["anomalies"]:
                st.write("Aucune anomalie.")
            for anomalie in evaluation["anomalies"]:
                libelle_gravite, couleur_gravite = _LIBELLES_GRAVITE.get(
                    anomalie["gravite"], (anomalie["gravite"], "gray")
                )
                st.markdown(f"- {_badge(libelle_gravite, couleur_gravite)} {anomalie['message']}")




                
# """Page Streamlit du dossier persistant (CONCEPTION_V2.md §2, §5, §8, §9).

# Remplace l'ancien formulaire à usage unique (V1, stateless) par un tableau
# de bord des dossiers, un formulaire de remplissage progressif, le
# déclenchement d'évaluations et la consultation de leur historique.
# """

# import os

# import requests
# import streamlit as st

# API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# st.set_page_config(page_title="Dossiers de création", layout="wide")
# st.title("Mes dossiers de création de SARL / SARL AU")

# if not st.session_state.get("jeton_acces"):
#     st.warning("Veuillez vous connecter depuis la page d'accueil pour accéder à vos dossiers.")
#     st.stop()

# en_tete = {"Authorization": f"Bearer {st.session_state.jeton_acces}"}


# def _appel(methode, chemin, **kwargs):
#     try:
#         reponse = requests.request(
#             methode, f"{API_BASE_URL}{chemin}", headers=en_tete, timeout=30, **kwargs
#         )
#         reponse.raise_for_status()
#         return reponse.json(), None
#     except requests.RequestException as exc:
#         detail = ""
#         try:
#             detail = exc.response.json().get("detail", "") if exc.response is not None else ""
#         except Exception:  # noqa: BLE001 - affichage best-effort de l'erreur API
#             detail = ""
#         return None, detail or str(exc)


# # --- Tableau de bord (CONCEPTION_V2.md §9.1) ------------------------------
# st.subheader("Tableau de bord")
# dossiers, erreur = _appel("GET", "/dossiers")
# if erreur:
#     st.error(f"Impossible de charger vos dossiers : {erreur}")
#     dossiers = []

# if dossiers:
#     for d in dossiers:
#         with st.container(border=True):
#             colonnes = st.columns([3, 2, 2, 2, 2])
#             colonnes[0].markdown(f"**{d['nom_projet']}** ({d['forme_juridique']})")
#             colonnes[1].metric("Statut", d["statut"])
#             colonnes[2].metric("Erreurs bloquantes", d["nb_erreurs_bloquantes"])
#             colonnes[3].metric("Avertissements", d["nb_avertissements"])
#             colonnes[4].metric("Progression", f"{d['progression_pct']}%")
#             if d["pret_pour_depot"]:
#                 st.success("Prêt pour dépôt")
#             if d["date_derniere_evaluation"]:
#                 st.caption(f"Dernière évaluation : {d['date_derniere_evaluation']}")
# else:
#     st.info("Aucun dossier pour l'instant. Créez-en un ci-dessous.")

# st.divider()

# # --- Création d'un nouveau dossier -----------------------------------------
# st.subheader("Créer un nouveau dossier")
# with st.form("formulaire_creation_dossier"):
#     nom_projet = st.text_input("Nom du projet")
#     forme_juridique = st.selectbox("Forme juridique", ["SARL", "SARL AU"])
#     capital_social = st.number_input("Capital social (DH)", min_value=1.0, step=1000.0)
#     siege_social = st.text_input("Siège social")
#     valide_creation = st.form_submit_button("Créer le dossier")

# if valide_creation:
#     payload = {
#         "nom_projet": nom_projet,
#         "forme_juridique": forme_juridique,
#         "capital_social": capital_social,
#         "siege_social": siege_social,
#     }
#     resultat, erreur = _appel("POST", "/dossiers", json=payload)
#     if erreur:
#         st.error(f"Création refusée : {erreur}")
#     else:
#         st.success(f"Dossier « {resultat['nom_projet']} » créé.")
#         st.rerun()

# st.divider()

# # --- Remplissage progressif, identités, évaluation --------------------------
# st.subheader("Compléter et évaluer un dossier")

# if not dossiers:
#     st.stop()

# options = {d["nom_projet"]: d["id"] for d in dossiers}
# choix_nom = st.selectbox("Dossier à compléter", list(options.keys()))
# dossier_id = options[choix_nom]
# dossier_courant = next(d for d in dossiers if d["id"] == dossier_id)

# with st.form("formulaire_maj_dossier"):
#     st.markdown("**Informations générales**")
#     statuts_fournis = st.checkbox("Statuts fournis", value=dossier_courant["statuts_fournis"])
#     certificat_negatif_fourni = st.checkbox(
#         "Certificat négatif fourni", value=dossier_courant["certificat_negatif_fourni"]
#     )
#     attestation_blocage = st.checkbox(
#         "Attestation de blocage bancaire fournie",
#         value=dossier_courant["attestation_blocage_bancaire_fournie"],
#     )
#     taxe_pro = st.checkbox(
#         "Taxe professionnelle déclarée", value=dossier_courant["taxe_professionnelle_declaree"]
#     )
#     emploie_salaries = st.checkbox(
#         "L'entreprise emploiera des salariés", value=dossier_courant["emploie_salaries"]
#     )
#     affiliation_cnss = st.checkbox(
#         "Affiliation CNSS fournie", value=dossier_courant["affiliation_cnss_fournie"]
#     )
#     valide_maj = st.form_submit_button("Enregistrer")

# if valide_maj:
#     payload = {
#         "statuts_fournis": statuts_fournis,
#         "certificat_negatif_fourni": certificat_negatif_fourni,
#         "attestation_blocage_bancaire_fournie": attestation_blocage,
#         "taxe_professionnelle_declaree": taxe_pro,
#         "emploie_salaries": emploie_salaries,
#         "affiliation_cnss_fournie": affiliation_cnss,
#     }
#     _, erreur = _appel("PATCH", f"/dossiers/{dossier_id}", json=payload)
#     if erreur:
#         st.error(f"Mise à jour refusée : {erreur}")
#     else:
#         st.success("Dossier mis à jour.")
#         st.rerun()

# st.markdown("**Associés (identités)**")
# with st.form("formulaire_identite"):
#     colonnes = st.columns(4)
#     nom = colonnes[0].text_input("Nom")
#     prenom = colonnes[1].text_input("Prénom")
#     numero_cin = colonnes[2].text_input("Numéro CIN")
#     date_naissance = colonnes[3].date_input("Date de naissance", value=None)
#     valide_identite = st.form_submit_button("Ajouter cet associé")

# if valide_identite:
#     payload = {
#         "nom": nom,
#         "prenom": prenom,
#         "numero_cin": numero_cin,
#         "date_naissance": str(date_naissance) if date_naissance else None,
#     }
#     _, erreur = _appel("POST", f"/dossiers/{dossier_id}/identites", json=payload)
#     if erreur:
#         st.error(f"Ajout refusé : {erreur}")
#     else:
#         st.success("Associé ajouté.")
#         st.rerun()

# st.markdown("**Évaluation**")
# if st.button("Lancer une évaluation"):
#     resultat, erreur = _appel("POST", f"/dossiers/{dossier_id}/evaluer")
#     if erreur:
#         st.error(f"Évaluation impossible : {erreur}")
#     else:
#         st.success(f"Verdict : {resultat['statut_global']}")
#         for anomalie in resultat["anomalies"]:
#             niveau_affichage = "🔴" if anomalie["gravite"] == "bloquante" else "🟡"
#             st.write(f"{niveau_affichage} **{anomalie['message']}**")
#             st.caption(
#                 f"Justification : {anomalie['justification']} — Source : "
#                 f"{anomalie['reference_documentaire']} (niveau {anomalie['niveau_documentaire']})"
#             )

# st.markdown("**Historique des évaluations**")
# historique, erreur = _appel("GET", f"/dossiers/{dossier_id}/evaluations")
# if erreur:
#     st.error(f"Historique indisponible : {erreur}")
# elif not historique:
#     st.info("Aucune évaluation pour l'instant.")
# else:
#     for evaluation in historique:
#         with st.expander(f"{evaluation['date_evaluation']} — {evaluation['statut_global']}"):
#             if not evaluation["anomalies"]:
#                 st.write("Aucune anomalie.")
#             for anomalie in evaluation["anomalies"]:
#                 st.write(f"- [{anomalie['gravite']}] {anomalie['message']}")
