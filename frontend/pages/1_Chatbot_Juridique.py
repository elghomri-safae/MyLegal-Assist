
"""Page Streamlit du chatbot juridique (RAG + compagnon du dossier, CONCEPTION_V2.md §6).

MODIFICATION (raccordement au pipeline RAG finalisé) : les citations
n'exposent plus de "niveau" documentaire significatif (toujours ``None``
côté API désormais, cf. ``backend/rag/generation.py`` — décision actée de
ne pas introduire de hiérarchie artificielle). L'affichage utilise
maintenant l'article, la page et la provenance du document, avec le même
langage visuel que le reste de l'application (``tag()`` de ``theme.py``)
plutôt qu'une simple légende texte.

MODIFICATION (timeout) : le timeout de l'appel ``/chat`` est passé de 60 à
180s. Les modèles (embeddings, reranker) sont chargés en mémoire au premier
appel après un (re)démarrage de l'API (mis en cache ensuite, cf.
``routers/chat.py``) — ce chargement initial peut à lui seul dépasser 60s,
faisant échouer la toute première question de chaque redémarrage. Idéalement
à précharger au démarrage d'uvicorn (``@app.on_event("startup")`` dans
``backend/main.py``) plutôt que de compter sur un timeout plus long côté
client — non fait ici faute d'avoir vu ``main.py``.
"""

import os

import requests
import streamlit as st

from theme import entete_plateforme, injecter_theme, note_pedagogique, tag

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Chatbot juridique — MyLegal Assist", layout="wide")
injecter_theme()
entete_plateforme("Chatbot juridique")

note_pedagogique(
    "Les réponses générales sont produites uniquement à partir du corpus documentaire "
    "fermé (Code de commerce, Loi 5-96, Loi 17-95, Loi 114-13, Loi 88-17, OMPIC, CNSS, "
    "DGI), avec citation systématique du document, de l'article et de la page lorsqu'ils "
    "sont disponibles. Si vous sélectionnez un dossier, le chatbot répond d'abord à "
    "partir de son état réel, et ne mobilise le corpus que pour les explications "
    "juridiques."
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
# a ajouter
with st.expander(" Historique de vos questions", expanded=False):
    try:
        params = {"dossier_id": dossier_id_selectionne} if dossier_id_selectionne else {}
        reponse_historique = requests.get(
            f"{API_BASE_URL}/chat/historique", headers=en_tete, params=params, timeout=15
        )
        reponse_historique.raise_for_status()
        historique_persiste = reponse_historique.json()
    except requests.RequestException as exc:
        st.error(f"Impossible de charger l'historique : {exc}")
        historique_persiste = []

    if not historique_persiste:
        st.caption("Aucune question posée pour l'instant.")
    else:
        for echange in historique_persiste:
            st.markdown(f"**Q — {echange['date'][:16].replace('T', ' ')}**")
            st.write(echange["texte"])
            if echange.get("reponse_texte"):
                st.markdown("**Réponse :**")
                st.write(echange["reponse_texte"])
                for citation in echange.get("citations", []):
                    st.caption(f"— {citation.get('document', '')} : {citation.get('reference', '')}")
            st.divider()
# 
if "historique_chat" not in st.session_state:
    st.session_state.historique_chat = []


def _afficher_citations(citations: list[dict]) -> None:
    """Affiche les citations d'une réponse avec le langage visuel du thème
    (étiquette façon tampon administratif pour la provenance, référence en
    dessous). N'affiche plus de "niveau" : ce champ n'est plus renseigné."""
    if not citations:
        return
    for citation in citations:
        st.markdown(
            f'{tag(citation.get("provenance") or "Source non renseignée")} '
            f'{citation["reference"]}',
            unsafe_allow_html=True,
        )


for question, reponse in st.session_state.historique_chat:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        st.write(reponse.get("texte", ""))
        _afficher_citations(reponse.get("citations", []))

question = st.chat_input("Posez votre question sur la création de SARL/SARL AU au Maroc…")

if question:
    with st.chat_message("user"):
        st.write(question)

    payload = {"texte": question, "dossier_id": dossier_id_selectionne}
    try:
        reponse_http = requests.post(
            f"{API_BASE_URL}/chat", json=payload, headers=en_tete, timeout=240
        )
        reponse_http.raise_for_status()
        reponse = reponse_http.json()
    except requests.RequestException as exc:
        reponse = {"texte": f"Erreur lors de l'appel à l'API : {exc}", "citations": []}

    with st.chat_message("assistant"):
        st.write(reponse.get("texte", ""))
        _afficher_citations(reponse.get("citations", []))

    st.session_state.historique_chat.append((question, reponse))
