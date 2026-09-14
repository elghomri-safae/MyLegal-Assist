"""Page Streamlit du dossier persistant (CONCEPTION_V2.md §2, §5, §8, §9).

Interface premium : cartes documents pédagogiques, synthèse par catégorie
avant le détail, badges sobres sans emoji, cartes d'anomalies avec
justification et source juridique. Aucune logique métier modifiée : cette
page ne fait qu'afficher et transmettre les données déjà exposées par
l'API existante (routes, schémas et règles inchangés).

Cette page est un outil de préparation destiné aux entrepreneurs avant le
rendez-vous chez MyLegal. Le système ne vérifie pas les documents
originaux : il évalue uniquement les informations déclarées.

MODIFICATION (référentiel documentaire — répartition des responsabilités) :
chaque pièce du catalogue porte désormais un badge "À fournir par vous"
(client) ou "Pris en charge par MyLegal" (cabinet/administration), d'après
le référentiel documentaire fourni. PUREMENT DE L'AFFICHAGE : aucune règle
du système expert, aucune sévérité, aucun comportement bloquant n'est
modifié par ce changement — seule l'étiquette pédagogique change.

MODIFICATION (retrait de la date de délivrance côté client) : le client
n'a plus de case à cocher pour confirmer disposer du certificat négatif
(pièce "cabinet", obtenue par MyLegal) — lui laisser saisir une date de
délivrance qu'il ne connaît généralement pas n'avait plus de sens. Le
champ reste en base (utile pour une future interface d'administration
côté cabinet), mais n'est plus proposé à la saisie ici.

MODIFICATION (visibilité du capital social) : le capital social, saisi
uniquement à la création du dossier, n'était ensuite plus ni affiché ni
modifiable — corrigé par l'ajout d'un champ éditable dans la section de
complétion.

MODIFICATION (liste des associés déjà enregistrés) : jusqu'ici, aucun
moyen de voir les associés déjà ajoutés à un dossier, ce qui a permis un
doublon non détecté en test. Ajout d'un affichage de la liste avant le
formulaire d'ajout (la détection du doublon lui-même est gérée côté API,
backend/services/dossier_service.py::ajouter_identite).
"""

import os

import requests
import streamlit as st

from theme import badge, entete_plateforme, injecter_theme, note_pedagogique, tag
from datetime import date, timedelta

# Calcul automatique : on ne peut pas choisir une date après le 1er janvier de l'année où l'on a eu 18 ans
date_limite = date.today() - timedelta(days=365*18)  # 18 ans révolus

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# --- Répartition des responsabilités (référentiel documentaire) ------------
# "client"  = 🟢 pièce dont seul le client détient l'original/l'information
# "cabinet" = 🟠 pièce produite/obtenue par le cabinet ou une administration,
#             ne devant jamais être présentée comme une faute du client
_RESPONSABLE_BADGE = {
    "client": ("À fournir par vous", "success"),
    "cabinet": ("Pris en charge par MyLegal", "warning"),
}


def _badge_responsable(cle_responsable: str) -> str:
    libelle, variante = _RESPONSABLE_BADGE[cle_responsable]
    return badge(libelle, variante)


# --- Catalogue des pièces du dossier, sous forme de cartes d'information ---
DOCUMENTS = [
    {
        "cle": "statuts",
        "nom": "Statuts de la société",
        "organisme": "Associés / rédacteur",
        "description": "Acte fondateur de la société, signé par l'ensemble des associés.",
        "pourquoi": "Fixe les règles de fonctionnement de la société et conditionne la validité de sa constitution.",
        "libelle_checkbox": "Je confirme disposer des statuts signés par l'ensemble des associés.",
    },
    {
        "cle": "attestation_blocage_bancaire",
        "nom": "Attestation de blocage bancaire",
        "organisme": "Banque",
        "description": "Justificatif du dépôt du capital libéré sur un compte bloqué.",
        "pourquoi": "Obligatoire lorsque le capital social dépasse 100 000 DH.",
        "libelle_checkbox": "Je confirme disposer de cette attestation (si applicable).",
    },
    {
        "cle": "affiliation_cnss",
        "nom": "Affiliation CNSS",
        "organisme": "CNSS",
        "description": "Numéro d'affiliation de l'entreprise employeuse.",
        "pourquoi": "Obligation légale pour toute entreprise employant des salariés.",
        "libelle_checkbox": "Je confirme disposer du numéro d'affiliation CNSS (si applicable).",
    },
    {
        "cle": "certificat_negatif",
        "nom": "Certificat négatif",
        "organisme": "OMPIC",
        "description": "Réservation officielle du nom de la société.",
        "pourquoi": "Permet de réserver le nom commercial avant l'immatriculation.",
        "libelle_checkbox": "Je confirme disposer d'un certificat négatif.",
    },
    {
        "cle": "taxe_professionnelle",
        "nom": "Déclaration à la taxe professionnelle",
        "organisme": "DGI",
        "description": "Déclaration d'inscription requise pour l'immatriculation.",
        "pourquoi": "Fait partie des documents à présenter au registre de commerce.",
        "libelle_checkbox": "Je confirme disposer de cette déclaration.",
    },
]

# Correspondance entre le type_piece (utilisé par DOCUMENTS) et le nom du
# champ booléen tel qu'exposé par DossierRead (API) — uniquement pour les
# pièces "client" qui ont une case à cocher. Les pièces "cabinet" n'ont
# pas de champ correspondant côté API.
_CHAMP_API_PAR_TYPE_PIECE = {
    "statuts": "statuts_fournis",
    "attestation_blocage_bancaire": "attestation_blocage_bancaire_fournie",
}


CARTE_IDENTITE = {
    "nom": "Pièce d'identité de chaque associé",
    "organisme": "CIN / Passeport",
    "description": "Carte d'identité nationale ou passeport de chaque associé.",
    "pourquoi": "Exigée pour la demande de certificat négatif et pour l'immatriculation.",
}

CARTE_SIEGE_SOCIAL = {
    "nom": "Justificatif de siège social",
    "organisme": "Bailleur / domiciliataire",
    "description": "Contrat de bail commercial ou contrat de domiciliation.",
    "pourquoi": (
        "Doit figurer dans les statuts ; détermine le tribunal et le centre des impôts "
        "compétents."
    ),
    "responsable": "client",
}

NOTE_DOCUMENTS = (
    "Cette étape permet de vérifier que vous disposez des pièces nécessaires avant de "
    "déposer votre dossier auprès de MyLegal. Cochez uniquement les documents que vous "
    "avez réellement en votre possession. Le badge sur chaque pièce indique si elle est "
    "à fournir par vous, ou prise en charge par MyLegal."
)
NOTE_EVALUATION = (
    "Cette évaluation est une pré-vérification pédagogique, basée sur les informations "
    "que vous avez déclarées. Elle ne remplace pas le contrôle des documents originaux, "
    "qui sera effectué par les juristes de MyLegal lors de votre rendez-vous."
)

_VARIANTE_VERDICT = {
    "conforme": ("Conforme", "success"),
    "conforme_avec_reserves": ("Attention", "warning"),
    "non_conforme": ("Non conforme", "danger"),
}
_VARIANTE_GRAVITE = {
    "bloquante": ("Non conforme", "danger"),
    "avertissement": ("Attention", "warning"),
    "informative": ("Information", "neutral"),
}
_CATEGORIES_SYNTHESE = [
    ("ID-", "Associés"),
    ("DOC-", "Documents obligatoires"),
    ("CAP-", "Capital"),
    ("FISC-", "Fiscalité"),
    ("CNSS-", "CNSS"),
]
_ORDRE_GRAVITE = {"bloquante": 2, "avertissement": 1, "informative": 0}


def _statut_categorie(anomalies: list, prefixe: str) -> tuple[str, str]:
    pertinentes = [a for a in anomalies if a["regle_id"].startswith(prefixe)]
    if not pertinentes:
        return ("Conforme", "success")
    plus_grave = max(pertinentes, key=lambda a: _ORDRE_GRAVITE.get(a["gravite"], 0))
    return _VARIANTE_GRAVITE.get(plus_grave["gravite"], (plus_grave["gravite"], "neutral"))


st.set_page_config(page_title="Dossiers de création — MyLegal Assist", layout="wide")
injecter_theme()
entete_plateforme("Évaluation de dossier")

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
        except Exception:
            detail = ""
        return None, detail or str(exc)


@st.cache_data(ttl=300)
def _charger_classification_pieces() -> dict[str, str]:
    resultat, erreur = _appel("GET", "/dossiers/classification-pieces")
    if erreur or resultat is None:
        return {}
    return {item["type_piece"]: item["responsable"] for item in resultat}


_CLASSIFICATION_PIECES = _charger_classification_pieces()


def get_responsable(type_piece: str) -> str:
    return _CLASSIFICATION_PIECES.get(type_piece, "client")


# --- Tableau de bord --------------------------------------------------------
st.subheader("Mes dossiers")
dossiers, erreur = _appel("GET", "/dossiers")
if erreur:
    st.error(f"Impossible de charger vos dossiers : {erreur}")
    dossiers = []

if dossiers:
    colonnes_dashboard = st.columns(min(len(dossiers), 3) or 1)
    for i, d in enumerate(dossiers):
        with colonnes_dashboard[i % len(colonnes_dashboard)]:
            with st.container(border=True):
                st.markdown(f'<div class="jr-card-title">{d["nom_projet"]}</div>', unsafe_allow_html=True)
                st.caption(d["forme_juridique"])
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
    valide_creation = st.form_submit_button("Créer le dossier", icon=":material/add_circle:")

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

# --- Sélection du dossier à compléter ---------------------------------------
st.subheader("Compléter et évaluer un dossier")
if not dossiers:
    st.stop()

options = {d["nom_projet"]: d["id"] for d in dossiers}
choix_nom = st.selectbox("Dossier à compléter", list(options.keys()))
dossier_id = options[choix_nom]
dossier_courant = next(d for d in dossiers if d["id"] == dossier_id)

# --- Siège social et capital -------------------------------------------------
note_pedagogique(
    "Renseignez ci-dessous l'adresse de votre siège social, le capital social et les "
    "pièces dont vous disposez déjà. Vous pourrez revenir compléter ce dossier à tout "
    "moment."
)

with st.container(border=True):
    colonne_info, colonne_action = st.columns([2, 1])
    with colonne_info:
        entete_col, badge_col = st.columns([3, 2])
        with entete_col:
            st.markdown(tag(CARTE_SIEGE_SOCIAL["organisme"]), unsafe_allow_html=True)
        with badge_col:
            st.markdown(_badge_responsable(CARTE_SIEGE_SOCIAL["responsable"]), unsafe_allow_html=True)
        st.markdown(f'<div class="jr-card-title">{CARTE_SIEGE_SOCIAL["nom"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="jr-card-desc">{CARTE_SIEGE_SOCIAL["description"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="jr-card-label">Pourquoi ?</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="jr-card-desc">{CARTE_SIEGE_SOCIAL["pourquoi"]}</div>', unsafe_allow_html=True)
    with colonne_action:
        siege_social_saisi = st.text_input(
            "Adresse du siège social", value=dossier_courant["siege_social"], key="siege_social_input"
        )
        capital_social_saisi = st.number_input(
            "Capital social (DH)",
            min_value=1.0,
            step=1000.0,
            value=float(dossier_courant["capital_social"]),
            key="capital_social_input",
        )
        _OPTIONS_JUSTIFICATIF_SIEGE = {
            "": "— Sélectionnez —",
            "bail": "Contrat de bail commercial",
            "domiciliation_myLegal": "Domiciliation par MyLegal",
            "domiciliation_tiers": "Domiciliation par un tiers agréé",
            "propriete": "Certificat de propriété",
        }
        type_justificatif_siege_saisi = st.selectbox(
            "Type de justificatif de siège",
            list(_OPTIONS_JUSTIFICATIF_SIEGE.keys()),
            format_func=lambda cle: _OPTIONS_JUSTIFICATIF_SIEGE[cle],
            index=list(_OPTIONS_JUSTIFICATIF_SIEGE.keys()).index(
                dossier_courant.get("type_justificatif_siege") or ""
            ),
            key="type_justificatif_siege_input",
        )
        if type_justificatif_siege_saisi == "domiciliation_myLegal":
            st.markdown(_badge_responsable("cabinet"), unsafe_allow_html=True)
        elif type_justificatif_siege_saisi:
            st.markdown(_badge_responsable("client"), unsafe_allow_html=True)

# --- Cartes documents --------------------------------------------------------
valeurs_documents: dict[str, bool] = {}
grille = st.columns(2)
for indice, document in enumerate(DOCUMENTS):
    with grille[indice % 2]:
        with st.container(border=True):
            responsable = get_responsable(document["cle"])
            entete_col, badge_col = st.columns([3, 2])
            with entete_col:
                st.markdown(tag(document["organisme"]), unsafe_allow_html=True)
            with badge_col:
                st.markdown(_badge_responsable(responsable), unsafe_allow_html=True)
            st.markdown(f'<div class="jr-card-title">{document["nom"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="jr-card-desc">{document["description"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="jr-card-label">Pourquoi ?</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="jr-card-desc">{document["pourquoi"]}</div>', unsafe_allow_html=True)
            st.divider()
            if responsable == "client":
                champ_api = _CHAMP_API_PAR_TYPE_PIECE.get(document["cle"])
                if champ_api:
                    valeur = dossier_courant.get(champ_api, False)
                else:
                    valeur = False
                valeurs_documents[document["cle"]] = st.checkbox(
                    document["libelle_checkbox"],
                    value=valeur,
                    key=f"checkbox_{document['cle']}",
                )
            else:
                st.caption(
                    "MyLegal se charge de cette formalité — aucune action requise de "
                    "votre part sur cette page."
                )

emploie_salaries_saisi = st.checkbox(
    "L'entreprise emploiera des salariés", value=dossier_courant["emploie_salaries"]
)

st.markdown("###### Gérance et capital")
gerant_designe_saisi = st.checkbox(
    "Le gérant est déjà désigné nommément dans les statuts",
    value=dossier_courant.get("gerant_designe_dans_statuts", False),
    help=(
        "Si non coché, un procès-verbal de nomination séparé sera nécessaire — "
        "MyLegal le rédige, ce n'est pas un document à fournir vous-même."
    ),
)

if st.button("Enregistrer les informations du dossier", icon=":material/save:"):
    payload_pieces = {
        _CHAMP_API_PAR_TYPE_PIECE[cle]: valeur for cle, valeur in valeurs_documents.items()
        if cle in _CHAMP_API_PAR_TYPE_PIECE
    }
    payload = {
        "siege_social": siege_social_saisi,
        "capital_social": capital_social_saisi,
        "emploie_salaries": emploie_salaries_saisi,
        "type_justificatif_siege": type_justificatif_siege_saisi,
        "gerant_designe_dans_statuts": gerant_designe_saisi,
        **payload_pieces,
    }
    _, erreur = _appel("PATCH", f"/dossiers/{dossier_id}", json=payload)
    if erreur:
        st.error(f"Mise à jour refusée : {erreur}")
    else:
        st.success("Dossier mis à jour.")
        st.rerun()

st.divider()

# --- Associés (identités) -----------------------------------------------------
st.subheader("Associés")
note_pedagogique(
    "Ajoutez ici l'identité de chaque associé de la société. Ces informations seront "
    "reprises dans les statuts et le dossier d'immatriculation."
)
with st.container(border=True):
    entete_col, badge_col = st.columns([3, 2])
    with entete_col:
        st.markdown(tag(CARTE_IDENTITE["organisme"]), unsafe_allow_html=True)
    with badge_col:
        st.markdown(_badge_responsable(get_responsable("cin")), unsafe_allow_html=True)
    st.markdown(f'<div class="jr-card-title">{CARTE_IDENTITE["nom"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="jr-card-desc">{CARTE_IDENTITE["description"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="jr-card-label">Pourquoi ?</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="jr-card-desc">{CARTE_IDENTITE["pourquoi"]}</div>', unsafe_allow_html=True)

if dossier_courant.get("identites"):
    st.markdown("###### Associés déjà enregistrés")
    for identite in dossier_courant["identites"]:
        with st.expander(f'{identite["nom"]} {identite["prenom"]} — CIN : {identite["numero_cin"]}'):
            with st.form(f"formulaire_modif_{identite['id']}"):
                colonnes_mod = st.columns(4)
                nom_mod = colonnes_mod[0].text_input("Nom", value=identite["nom"] or "")
                prenom_mod = colonnes_mod[1].text_input("Prénom", value=identite["prenom"] or "")
                cin_mod = colonnes_mod[2].text_input("Numéro CIN", value=identite["numero_cin"] or "")
                date_naissance_actuelle = (
                    identite["date_naissance"] if identite.get("date_naissance") else None
                )
                date_naissance_mod = colonnes_mod[3].date_input(
                    "Date de naissance", value=date_naissance_actuelle
                )

                colonnes_apport_mod = st.columns(2)
                type_apport_mod = colonnes_apport_mod[0].selectbox(
                    "Type d'apport",
                    ["", "numeraire", "nature"],
                    index=["", "numeraire", "nature"].index(
                        identite.get("type_apport_personnel") or ""
                    ),
                    format_func=lambda v: {
                        "": "— Non renseigné —", "numeraire": "Numéraire", "nature": "Nature"
                    }[v],
                )
                montant_mod = colonnes_apport_mod[1].number_input(
                    "Montant de l'apport (DH)",
                    min_value=0.0,
                    step=1000.0,
                    value=float(identite.get("montant_apport") or 0),
                )

                col_valider, col_supprimer = st.columns(2)
                valide_modif = col_valider.form_submit_button(
                    "Enregistrer les modifications", icon=":material/save:"
                )
                valide_suppr = col_supprimer.form_submit_button(
                    "Supprimer cet associé", icon=":material/delete:", type="secondary"
                )

            if valide_modif:
                payload_mod = {
                    "nom": nom_mod,
                    "prenom": prenom_mod,
                    "numero_cin": cin_mod,
                    "date_naissance": str(date_naissance_mod) if date_naissance_mod else None,
                    "type_apport_personnel": type_apport_mod or None,
                    "montant_apport": montant_mod if montant_mod > 0 else None,
                }
                _, erreur = _appel(
                    "PATCH", f"/dossiers/{dossier_id}/identites/{identite['id']}", json=payload_mod
                )
                if erreur:
                    st.error(f"Modification refusée : {erreur}")
                else:
                    st.success("Associé modifié.")
                    st.rerun()

            if valide_suppr:
                _, erreur = _appel("DELETE", f"/dossiers/{dossier_id}/identites/{identite['id']}")
                if erreur:
                    st.error(f"Suppression refusée : {erreur}")
                else:
                    st.success("Associé supprimé.")
                    st.rerun()
    st.divider()

with st.form("formulaire_identite"):
    colonnes = st.columns(4)
    nom = colonnes[0].text_input("Nom")
    prenom = colonnes[1].text_input("Prénom")
    numero_cin = colonnes[2].text_input("Numéro CIN")
    date_naissance = colonnes[3].date_input(
        "Date de naissance", 
        value=None,
        min_value=date(1900, 1, 1),
        max_value=date_limite,
        help="Saisissez une date au format AAAA-MM-JJ (ex: 1980-01-01)"
    )

    colonnes_apport = st.columns(2)
    type_apport_personnel = colonnes_apport[0].selectbox(
        "Type d'apport de cet associé",
        ["", "numeraire", "nature"],
        format_func=lambda v: {"": "— Non renseigné —", "numeraire": "Numéraire", "nature": "Nature"}[v],
        help="Un seul associé en apport nature suffit à rediriger tout le dossier vers un traitement manuel.",
    )
    montant_apport = colonnes_apport[1].number_input(
        "Montant de l'apport (DH)", min_value=0.0, step=1000.0, value=0.0
    )

    valide_identite = st.form_submit_button("Ajouter cet associé", icon=":material/person_add:")

if valide_identite:
    payload = {
        "nom": nom,
        "prenom": prenom,
        "numero_cin": numero_cin,
        "date_naissance": str(date_naissance) if date_naissance else None,
        "type_apport_personnel": type_apport_personnel or None,
        "montant_apport": montant_apport if montant_apport > 0 else None,
    }
    _, erreur = _appel("POST", f"/dossiers/{dossier_id}/identites", json=payload)
    if erreur:
        st.error(f"Ajout refusée : {erreur}")
    else:
        st.success("Associé ajouté.")
        st.rerun()

st.divider()

# --- Évaluation et rapport ----------------------------------------------------
st.subheader("Évaluation du dossier")
note_pedagogique(NOTE_EVALUATION)

if "derniere_evaluation_par_dossier" not in st.session_state:
    st.session_state.derniere_evaluation_par_dossier = {}

if st.button("Lancer une évaluation", type="primary", icon=":material/fact_check:"):
    resultat, erreur = _appel("POST", f"/dossiers/{dossier_id}/evaluer")
    if erreur:
        st.error(f"Évaluation impossible : {erreur}")
    else:
        st.session_state.derniere_evaluation_par_dossier[dossier_id] = resultat
        st.rerun()

resultat_a_afficher = st.session_state.derniere_evaluation_par_dossier.get(dossier_id)
if resultat_a_afficher:
    anomalies = resultat_a_afficher["anomalies"]

    # --- Synthèse par catégorie (affichage clair en colonnes) ---
    st.markdown("#### Synthèse")
    with st.container(border=True):
        col_gauche, col_droite = st.columns([1, 1])
        
        with col_gauche:
            st.markdown("**Associés**")
            st.markdown("**Documents obligatoires**")
            st.markdown("**Capital**")
            st.markdown("**Fiscalité**")
            st.markdown("**CNSS**")
            st.markdown("---")
            st.markdown("**Verdict final**")
        
        with col_droite:
            for prefixe, _ in _CATEGORIES_SYNTHESE:
                libelle_statut, variante = _statut_categorie(anomalies, prefixe)
                st.markdown(badge(libelle_statut, variante), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Si le dossier est en "Hors périmètre", on affiche "Hors périmètre automatisé"
            if dossier_courant["statut"] == "hors_perimetre_automatise":
                libelle_verdict = "Hors périmètre automatisé"
                variante_verdict = "warning"
            else:
                libelle_verdict, variante_verdict = _VARIANTE_VERDICT.get(
                    resultat_a_afficher["statut_global"], (resultat_a_afficher["statut_global"], "neutral")
                )
            st.markdown(badge(libelle_verdict, variante_verdict), unsafe_allow_html=True)

    # --- Détail des anomalies, en cartes ---
    if anomalies:
        st.markdown("#### Détail")
        for anomalie in anomalies:
            libelle_gravite, variante_gravite = _VARIANTE_GRAVITE.get(
                anomalie["gravite"], (anomalie["gravite"], "neutral")
            )
            with st.container(border=True):
                st.markdown(tag(anomalie["regle_id"]), unsafe_allow_html=True)
                entete_col, badge_col = st.columns([4, 1])
                with entete_col:
                    st.markdown(
                        f'<div class="jr-card-title">{anomalie["message"]}</div>',
                        unsafe_allow_html=True,
                    )
                with badge_col:
                    st.markdown(badge(libelle_gravite, variante_gravite), unsafe_allow_html=True)
                st.markdown('<div class="jr-card-label">Justification juridique</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="jr-card-desc">{anomalie["justification"]}</div>', unsafe_allow_html=True)
                st.caption(
                    f"Source : {anomalie['reference_documentaire']} "
                    f"(niveau {anomalie['niveau_documentaire']})"
                )

st.divider()

# --- Historique des évaluations ----------------------------------------------
st.subheader("Historique des évaluations")
note_pedagogique(
    "Chaque évaluation lancée est conservée : vous pouvez suivre la progression de votre "
    "dossier au fil de vos corrections."
)
historique, erreur = _appel("GET", f"/dossiers/{dossier_id}/evaluations")
if erreur:
    st.error(f"Historique indisponible : {erreur}")
elif not historique:
    st.info("Aucune évaluation pour l'instant.")
else:
    for evaluation in historique:
        libelle, variante = _VARIANTE_VERDICT.get(
            evaluation["statut_global"], (evaluation["statut_global"], "neutral")
        )
        with st.expander(f"{evaluation['date_evaluation']} — {libelle}"):
            if not evaluation["anomalies"]:
                st.write("Aucune anomalie.")
            for anomalie in evaluation["anomalies"]:
                libelle_gravite, variante_gravite = _VARIANTE_GRAVITE.get(
                    anomalie["gravite"], (anomalie["gravite"], "neutral")
                )
                st.markdown(
                    f'{badge(libelle_gravite, variante_gravite)} &nbsp; {anomalie["message"]}',
                    unsafe_allow_html=True,
                )