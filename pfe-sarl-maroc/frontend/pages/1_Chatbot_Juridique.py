"""Page Streamlit du chatbot juridique (RAG + compagnon du dossier, CONCEPTION_V2.md §6)."""

import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Chatbot juridique", layout="wide")
st.title("Chatbot juridique — Création de SARL / SARL AU au Maroc")

st.caption(
    "Les réponses générales sont produites uniquement à partir du corpus documentaire "
    "fermé (Loi 5-96, OMPIC, DGI, Dar Al Moukawil, guide pratique), avec citation "
    "systématique de la source et de son niveau. Si vous sélectionnez un dossier, le "
    "chatbot répond d'abord à partir de son état réel (système expert), et ne mobilise "
    "le corpus que pour les explications juridiques."
)

if not st.session_state.get("jeton_acces"):
    st.warning("Veuillez vous connecter depuis la page d'accueil pour utiliser le chatbot.")
    st.stop()

en_tete = {"Authorization": f"Bearer {st.session_state.jeton_acces}"}

try:
    reponse_dossiers = requests.get(f"{API_BASE_URL}/dossiers", headers=en_tete, timeout=15)
    reponse_dossiers.raise_for_status()
    dossiers = reponse_dossiers.json()
except requests.RequestException:
    dossiers = []

options_dossier = {"— Question générale —": None}
options_dossier.update({d["nom_projet"]: d["id"] for d in dossiers})
choix = st.selectbox("Contexte de la question", list(options_dossier.keys()))
dossier_id_selectionne = options_dossier[choix]

if "historique_chat" not in st.session_state:
    st.session_state.historique_chat = []

for question, reponse in st.session_state.historique_chat:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        st.write(reponse.get("texte", ""))
        for citation in reponse.get("citations", []):
            st.caption(
                f"[{citation['document']}, Niveau {citation['niveau']}, "
                f"{citation['reference']}]"
            )

question = st.chat_input("Posez votre question sur la création de SARL/SARL AU au Maroc…")

if question:
    with st.chat_message("user"):
        st.write(question)

    payload = {"texte": question, "dossier_id": dossier_id_selectionne}
    try:
        reponse_http = requests.post(
            f"{API_BASE_URL}/chat", json=payload, headers=en_tete, timeout=60
        )
        reponse_http.raise_for_status()
        reponse = reponse_http.json()
    except requests.RequestException as exc:
        reponse = {"texte": f"Erreur lors de l'appel à l'API : {exc}", "citations": []}

    with st.chat_message("assistant"):
        st.write(reponse.get("texte", ""))
        for citation in reponse.get("citations", []):
            st.caption(
                f"[{citation['document']}, Niveau {citation['niveau']}, "
                f"{citation['reference']}]"
            )

    st.session_state.historique_chat.append((question, reponse))
