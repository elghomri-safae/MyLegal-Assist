"""Streamlit entrypoint - page d'accueil et connexion de l'assistant creation SARL Maroc."""

import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Assistant creation SARL Maroc", layout="wide")
st.title("Assistant de creation de SARL / SARL AU au Maroc")

st.write(
    "Cette interface donne acces a deux modules : le chatbot juridique et le "
    "systeme expert anti-rejet de dossier (voir le menu a gauche). Une connexion "
    "est requise pour utiliser ces modules (voir TODO.md pour l'etat d'avancement "
    "par phase)."
)

st.subheader("Etat du backend")
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    response.raise_for_status()
    st.success(f"API disponible : {response.json()}")
except requests.RequestException as exc:
    st.error(f"API indisponible : {exc}")

if "jeton_acces" not in st.session_state:
    st.session_state.jeton_acces = None
    st.session_state.utilisateur_email = None
    st.session_state.utilisateur_role = None

st.subheader("Connexion")

if st.session_state.jeton_acces:
    st.success(
        f"Connecte en tant que {st.session_state.utilisateur_email} "
        f"(role : {st.session_state.utilisateur_role})"
    )
    if st.button("Se deconnecter"):
        st.session_state.jeton_acces = None
        st.session_state.utilisateur_email = None
        st.session_state.utilisateur_role = None
        st.rerun()
else:
    onglet_connexion, onglet_inscription = st.tabs(["Se connecter", "Créer un compte"])

    with onglet_connexion:
        with st.form("formulaire_connexion"):
            email = st.text_input("Email", key="email_connexion")
            mot_de_passe = st.text_input("Mot de passe", type="password", key="mdp_connexion")
            valide = st.form_submit_button("Se connecter")
        if valide:
            try:
                reponse = requests.post(
                    f"{API_BASE_URL}/auth/connexion",
                    json={"email": email, "mot_de_passe": mot_de_passe},
                    timeout=10,
                )
                reponse.raise_for_status()
                jeton = reponse.json()["access_token"]

                import jwt as pyjwt

                charge_utile = pyjwt.decode(jeton, options={"verify_signature": False})
                st.session_state.jeton_acces = jeton
                st.session_state.utilisateur_email = charge_utile["email"]
                st.session_state.utilisateur_role = charge_utile["role"]
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"Connexion refusee : {exc}")

    with onglet_inscription:
        with st.form("formulaire_inscription"):
            nom = st.text_input("Nom")
            email_inscription = st.text_input("Email", key="email_inscription")
            mot_de_passe_inscription = st.text_input(
                "Mot de passe", type="password", key="mdp_inscription"
            )
            role = st.selectbox("Role", ["entrepreneur", "admin"])
            valide_inscription = st.form_submit_button("Créer le compte")
        if valide_inscription:
            try:
                reponse = requests.post(
                    f"{API_BASE_URL}/auth/inscription",
                    json={
                        "nom": nom,
                        "email": email_inscription,
                        "mot_de_passe": mot_de_passe_inscription,
                        "role": role,
                    },
                    timeout=10,
                )
                reponse.raise_for_status()
                st.success("Compte cree. Vous pouvez maintenant vous connecter.")
            except requests.RequestException as exc:
                st.error(f"Inscription refusee : {exc}")
