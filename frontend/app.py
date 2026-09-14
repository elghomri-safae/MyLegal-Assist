
# """Streamlit entrypoint - page d'accueil et connexion de l'assistant creation SARL Maroc.

# MODIFICATION (Phase 1 — comptes créés par MyLegal) : l'onglet "Créer un
# compte" (auto-inscription libre, y compris avec un rôle "admin" au choix du
# visiteur) est retiré — il appelait ``POST /auth/inscription``, supprimée
# côté API (cf. ``backend/routers/auth.py``) et remplacée par
# ``POST /auth/entrepreneurs``, réservée aux administrateurs (page
# "Administration"). Un visiteur non connecté ne peut donc plus que se
# connecter avec des identifiants déjà fournis par MyLegal.
# """

# import os

# import requests
# import streamlit as st

# from theme import entete_plateforme, injecter_theme, note_pedagogique

# API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


# st.set_page_config(page_title="Juris-IA — Assistant création SARL Maroc", layout="wide")
# injecter_theme()
# entete_plateforme("Accueil")

# note_pedagogique(
#     "Juris-IA vous accompagne dans la préparation de votre dossier de création de "
#     "SARL / SARL AU, avant votre rendez-vous chez MyLegal : vérification des pièces, "
#     "détection des points à corriger, et réponses à vos questions juridiques. Cette "
#     "plateforme ne dépose pas votre dossier : elle vous prépare à le faire dans les "
#     "meilleures conditions."
# )

# # st.subheader("Etat du backend")
# # try:
# #     response = requests.get(f"{API_BASE_URL}/health", timeout=5)
# #     response.raise_for_status()
# #     st.success(f"API disponible : {response.json()}")
# # except requests.RequestException as exc:
# #     st.error(f"API indisponible : {exc}")

# if "jeton_acces" not in st.session_state:
#     st.session_state.jeton_acces = None
#     st.session_state.utilisateur_email = None
#     st.session_state.utilisateur_role = None

# st.subheader("Connexion")

# if st.session_state.jeton_acces:
#     st.success(
#         f"Connecte en tant que {st.session_state.utilisateur_email} "
#         f"(role : {st.session_state.utilisateur_role})"
#     )
#     if st.button("Se deconnecter", icon=":material/logout:"):
#         st.session_state.jeton_acces = None
#         st.session_state.utilisateur_email = None
#         st.session_state.utilisateur_role = None
#         # Vide l'historique du chatbot à la déconnexion : sans ça, il reste
#         # visible tel quel pour le prochain utilisateur connecté dans le
#         # même onglet de navigateur (st.session_state est lié à la session
#         # du navigateur, pas à l'identité applicative) — bug de
#         # confidentialité réel, observé en conditions réelles.
#         st.session_state.historique_chat = []
#         st.rerun()
# else:
#     note_pedagogique(
#         "Les comptes sont créés par MyLegal : si vous êtes un nouveau client, "
#         "contactez MyLegal pour recevoir vos identifiants de connexion."
#     )
#     with st.form("formulaire_connexion"):
#         email = st.text_input("Email", key="email_connexion")
#         mot_de_passe = st.text_input("Mot de passe", type="password", key="mdp_connexion")
#         valide = st.form_submit_button("Se connecter", icon=":material/login:")
#     if valide:
#         try:
#             reponse = requests.post(
#                 f"{API_BASE_URL}/auth/connexion",
#                 json={"email": email, "mot_de_passe": mot_de_passe},
#                 timeout=10,
#             )
#             reponse.raise_for_status()
#             jeton = reponse.json()["access_token"]

#             import jwt as pyjwt

#             charge_utile = pyjwt.decode(jeton, options={"verify_signature": False})
#             st.session_state.jeton_acces = jeton
#             st.session_state.utilisateur_email = charge_utile["email"]
#             st.session_state.utilisateur_role = charge_utile["role"]
#             # Filet de sécurité : vide aussi l'historique à la CONNEXION (pas
#             # seulement à la déconnexion), pour le cas où un utilisateur se
#             # connecterait directement sans passer par "Se déconnecter"
#             # (fermeture d'onglet puis reconnexion dans le même onglet plus
#             # tard, etc.).
#             st.session_state.historique_chat = []
#             st.rerun()
#         except requests.RequestException as exc:
#             st.error(f"Connexion refusee : {exc}")


"""Streamlit entrypoint - page d'accueil et connexion de l'assistant creation SARL Maroc.

MODIFICATION (Phase 1 — comptes créés par MyLegal) : l'onglet "Créer un
compte" (auto-inscription libre, y compris avec un rôle "admin" au choix du
visiteur) est retiré — il appelait ``POST /auth/inscription``, supprimée
côté API (cf. ``backend/routers/auth.py``) et remplacée par
``POST /auth/entrepreneurs``, réservée aux administrateurs (page
"Administration"). Un visiteur non connecté ne peut donc plus que se
connecter avec des identifiants déjà fournis par MyLegal.
"""

import os

import requests
import streamlit as st

from theme import entete_plateforme, injecter_theme, note_pedagogique

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


st.set_page_config(page_title="MyLegal Assist — Connexion", layout="wide")
injecter_theme()
entete_plateforme("Connexion")

note_pedagogique(
    "Cette plateforme vous accompagne dans la préparation de votre dossier de création de "
    "SARL / SARL AU, avant votre rendez-vous chez MyLegal : vérification des pièces, "
    "détection des points à corriger, et réponses à vos questions juridiques. "
    "Elle ne dépose pas votre dossier : elle vous prépare à le faire dans les "
    "meilleures conditions."
)

# st.subheader("Etat du backend")
# try:
#     response = requests.get(f"{API_BASE_URL}/health", timeout=5)
#     response.raise_for_status()
#     st.success(f"API disponible : {response.json()}")
# except requests.RequestException as exc:
#     st.error(f"API indisponible : {exc}")

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
    if st.button("Se deconnecter", icon=":material/logout:"):
        st.session_state.jeton_acces = None
        st.session_state.utilisateur_email = None
        st.session_state.utilisateur_role = None
        # Vide l'historique du chatbot à la déconnexion : sans ça, il reste
        # visible tel quel pour le prochain utilisateur connecté dans le
        # même onglet de navigateur (st.session_state est lié à la session
        # du navigateur, pas à l'identité applicative) — bug de
        # confidentialité réel, observé en conditions réelles.
        st.session_state.historique_chat = []
        st.rerun()
else:
    note_pedagogique(
        "Les comptes sont créés par MyLegal : si vous êtes un nouveau client, "
        "contactez MyLegal pour recevoir vos identifiants de connexion."
    )
    with st.form("formulaire_connexion"):
        email = st.text_input("Email", key="email_connexion")
        mot_de_passe = st.text_input("Mot de passe", type="password", key="mdp_connexion")
        valide = st.form_submit_button("Se connecter", icon=":material/login:")
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
            # Filet de sécurité : vide aussi l'historique à la CONNEXION (pas
            # seulement à la déconnexion), pour le cas où un utilisateur se
            # connecterait directement sans passer par "Se déconnecter"
            # (fermeture d'onglet puis reconnexion dans le même onglet plus
            # tard, etc.).
            st.session_state.historique_chat = []
            st.rerun()
        except requests.RequestException as exc:
            st.error(f"Connexion refusee : {exc}")