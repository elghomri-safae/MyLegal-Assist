

"""Page Streamlit d'administration — réservée au rôle admin.

Consomme POST /auth/entrepreneurs (backend/routers/auth.py), protégé côté
API par exiger_role("admin") : cette page n'est qu'une façade, la vraie
barrière de sécurité est côté serveur (un appel direct à l'API avec un JWT
entrepreneur serait refusé avec 403, quel que soit ce que fait cette page).
Le contrôle ci-dessous (st.session_state.utilisateur_role) n'est qu'un
confort d'affichage : éviter de montrer un formulaire inutilisable.
"""

import os

import requests
import streamlit as st

from theme import badge, entete_plateforme, injecter_theme, note_pedagogique

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Administration — MyLegal Assist", layout="wide")
injecter_theme()
entete_plateforme("Administration")

if not st.session_state.get("jeton_acces"):
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

if st.session_state.get("utilisateur_role") != "admin":
    st.error(
        "Cette page est réservée au personnel MyLegal (rôle admin). "
        "Le serveur refuserait de toute façon toute action ici avec votre rôle actuel."
    )
    st.stop()

en_tete = {"Authorization": f"Bearer {st.session_state.jeton_acces}"}

note_pedagogique(
    "Créez ici le compte d'un nouveau client entrepreneur. Un mot de passe "
    "temporaire est généré automatiquement et affiché une seule fois "
    "ci-dessous : transmettez-le au client par un canal sécurisé (il ne "
    "sera plus jamais affiché après cette création)."
)



st.subheader("Créer un compte entrepreneur")

with st.form("formulaire_creation_entrepreneur"):
    nom = st.text_input("Nom complet du client")
    email = st.text_input("Email du client")
    valide = st.form_submit_button("Créer le compte", icon=":material/person_add:")

if valide:
    if not nom or not email:
        st.error("Nom et email sont obligatoires.")
    else:
        try:
            reponse = requests.post(
                f"{API_BASE_URL}/auth/entrepreneurs",
                json={"nom": nom, "email": email},
                headers=en_tete,
                timeout=15,
            )
            reponse.raise_for_status()
            resultat = reponse.json()

            st.success(f"Compte créé pour {resultat['email']}.")
            with st.container(border=True):
                st.markdown('<div class="jr-card-label">Identifiants à transmettre au client</div>', unsafe_allow_html=True)
                st.code(
                    f"Email : {resultat['email']}\n"
                    f"Mot de passe temporaire : {resultat['mot_de_passe_temporaire']}",
                    language=None,
                )
                st.caption(
                    "Ce mot de passe ne sera plus jamais affiché. Copiez-le maintenant."
                )
        except requests.RequestException as exc:
            detail = ""
            try:
                detail = exc.response.json().get("detail", "") if exc.response is not None else ""
            except Exception:  # noqa: BLE001 - affichage best-effort
                detail = ""
            st.error(f"Création refusée : {detail or exc}")

st.divider()

# --- Consultation de tous les dossiers (lecture seule) ----------------------
st.subheader("Dossiers de tous les clients")
note_pedagogique(
    "Vue de consultation uniquement : cette page ne permet ni de modifier, "
    "ni de relancer une évaluation sur le dossier d'un client. Pour toute "
    "correction, le client doit intervenir lui-même depuis son propre compte."
)

try:
    reponse_dossiers = requests.get(f"{API_BASE_URL}/admin/dossiers", headers=en_tete, timeout=15)
    reponse_dossiers.raise_for_status()
    dossiers_admin = reponse_dossiers.json()
except requests.RequestException as exc:
    st.error(f"Impossible de charger les dossiers : {exc}")
    dossiers_admin = []

if not dossiers_admin:
    st.info("Aucun dossier créé par les clients pour l'instant.")
else:
    for item in dossiers_admin:
        d = item["dossier"]
        with st.container(border=True):
            colonne_info, colonne_statut = st.columns([3, 1])
            with colonne_info:
                st.markdown(f'<div class="jr-card-title">{d["nom_projet"]}</div>', unsafe_allow_html=True)
                st.caption(f'{d["forme_juridique"]} — {item["entrepreneur_nom"]} ({item["entrepreneur_email"]})')
            with colonne_statut:
                libelle_statut, variante_statut = (
                    ("Prêt pour dépôt", "success")
                    if d["pret_pour_depot"]
                    else (d["statut"].capitalize(), "neutral")
                )
                st.markdown(badge(libelle_statut, variante_statut), unsafe_allow_html=True)
            st.markdown(
                f'<div class="jr-card-label">Progression</div> {d["progression_pct"]}%',
                unsafe_allow_html=True,
            )
            st.caption(
                f"{d['nb_erreurs_bloquantes']} erreur(s) bloquante(s) · "
                f"{d['nb_avertissements']} avertissement(s)"
            )
