
"""Thème visuel partagé de l'interface Streamlit (frontend uniquement).

Aucune logique métier ici : uniquement de l'injection CSS et de petits
gabarits HTML (badges, étiquettes d'organisme, notes pédagogiques) réutilisés
par toutes les pages. N'appelle aucune route API, ne dépend d'aucun modèle.

Identité visuelle retenue : un cabinet d'accompagnement juridique moderne.
Fond papier neutre, encre bleu nuit pour la hiérarchie de lecture, un accent
bronze utilisé avec parcimonie (rappel des tampons/références officielles
marocaines — OMPIC, DGI, CNSS), une police display sérif (Newsreader) pour
les titres, une police utilitaire (IBM Plex Sans/Mono) pour le contenu et
les références de pièces — ce dernier élément (l'étiquette de référence en
police mono, façon tampon administratif) est le fil conducteur visuel de
toute l'application.
"""


from __future__ import annotations

import streamlit as st

_CSS = (
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;"""
    """0,6..72,600;0,6..72,700;1,6..72,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:"""
    """wght@500;600&display=swap');

:root {
    --jr-bg: #F7F5EF;
    --jr-bg-deep: #F0EDE3;
    --jr-surface: #FFFFFF;
    --jr-ink: #17233B;
    --jr-ink-muted: #45505F;   /* était #5B6472 — plus sombre, meilleur contraste */
    --jr-ink-soft: #6B7280;    /* était #8B92A0 — plus lisible pour les petits libellés */
    --jr-border: #E4E0D2;
    --jr-border-soft: #ECE9DD;
    --jr-accent: #9C6B2B;
    --jr-accent-deep: #7C531F;
    --jr-accent-soft: #F3E7D2;
    --jr-success: #2F6D4C;
    --jr-success-bg: #E4EFE8;
    --jr-warning: #9C6B15;
    --jr-warning-bg: #FBF0DC;
    --jr-danger: #A6352C;
    --jr-danger-bg: #F8E6E2;
    --jr-neutral-bg: #ECEAE3;
    --jr-shadow: 0 1px 2px rgba(23, 35, 59, 0.04), 0 6px 20px rgba(23, 35, 59, 0.06);
    --jr-shadow-soft: 0 1px 3px rgba(23, 35, 59, 0.05);
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 1200px 600px at 15% -5%, rgba(156, 107, 43, 0.05), transparent),
        var(--jr-bg);
}
[data-testid="stHeader"] { background-color: transparent; }
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    color: var(--jr-ink);
    font-size: 16px;          /* ajout : base légèrement plus grande */
    line-height: 1.6;         /* ajout : meilleure aération du texte */
}
h1, h2, h3, [data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Newsreader', Georgia, serif !important;
    font-weight: 600 !important;
    color: var(--jr-ink) !important;
    letter-spacing: -0.015em;
}
[data-testid="stMarkdownContainer"] h4 {
    font-family: 'Newsreader', Georgia, serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    color: var(--jr-ink) !important;
    margin-bottom: 0.15rem !important;
}

.jr-masthead {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    border-bottom: 1px solid var(--jr-border);
    position: relative;
    padding-bottom: 1rem;
    margin-bottom: 1.6rem;
}
.jr-masthead::after {
    content: "";
    position: absolute;
    bottom: -1px; left: 0;
    width: 64px; height: 2px;
    background: linear-gradient(90deg, var(--jr-accent), transparent);
}
.jr-masthead__title {
    font-family: 'Newsreader', serif;
    font-weight: 600;
    font-size: 1.7rem;
    letter-spacing: -0.015em;
    color: var(--jr-ink);
}
.jr-masthead__tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--jr-accent-deep);
    background: var(--jr-accent-soft);
    border: 1px solid rgba(156, 107, 43, 0.25);
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
}

.jr-note {
    background: var(--jr-surface);
    border-left: 3px solid var(--jr-accent);
    border-radius: 0 12px 12px 0;
    padding: 0.95rem 1.2rem;
    margin: 0.5rem 0 1.3rem 0;
    color: var(--jr-ink-muted);
    .jr-note {
    font-size: 0.97rem;       /* était 0.93rem */
    line-height: 1.65;        /* était 1.6 */
    box-shadow: var(--jr-shadow-soft);
}

.jr-tag {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--jr-accent-deep);
    background: var(--jr-accent-soft);
    border: 1px solid rgba(156, 107, 43, 0.3);
    padding: 0.18rem 0.55rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
}

.jr-badge {
    display: inline-flex;
    align-items: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    white-space: nowrap;
    box-shadow: var(--jr-shadow-soft);
}
.jr-badge--success { background: var(--jr-success-bg); color: var(--jr-success); }
.jr-badge--warning { background: var(--jr-warning-bg); color: var(--jr-warning); }
.jr-badge--danger  { background: var(--jr-danger-bg);  color: var(--jr-danger); }
.jr-badge--neutral { background: var(--jr-neutral-bg); color: var(--jr-ink-muted); }

.jr-card-title {
    font-family: 'Newsreader', serif;
    font-weight: 600;
    font-size: 1.15rem;
    color: var(--jr-ink);
    margin: 0.1rem 0 0.35rem 0;
}
.jr-card-desc { color: var(--jr-ink-muted); font-size: 0.93rem; line-height: 1.55; }
.jr-card-label {
    font-size: 0.97rem;
    line-height: 1.6;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--jr-ink-soft);
    margin-top: 0.6rem;
}

.jr-synthese-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--jr-border-soft);
    font-size: 0.95rem;
}
.jr-synthese-item:last-child { border-bottom: none; }
.jr-synthese-verdict {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.2rem;
    margin-top: 0.7rem;
    background: linear-gradient(135deg, var(--jr-ink) 0%, #1F3055 100%);
    border-radius: 12px;
    color: #FFFFFF;
    font-family: 'Newsreader', serif;
    font-size: 1.2rem;
    font-weight: 600;
    box-shadow: var(--jr-shadow);
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border: 1px solid var(--jr-border) !important;
    background: var(--jr-surface) !important;
    box-shadow: var(--jr-shadow) !important;
    transition: box-shadow 0.2s ease;
}

button[kind="primary"], button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, var(--jr-ink) 0%, #1F3055 100%) !important;
    border-color: var(--jr-ink) !important;
    border-radius: 9px !important;
    box-shadow: var(--jr-shadow-soft);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
    transform: translateY(-1px);
    box-shadow: var(--jr-shadow);
}
button[kind="secondary"], button[kind="secondaryFormSubmit"] {
    border-radius: 9px !important;
    border-color: var(--jr-border) !important;
    transition: border-color 0.15s ease;
}
button[kind="secondary"]:hover, button[kind="secondaryFormSubmit"]:hover {
    border-color: var(--jr-accent) !important;
}

[data-testid="stTextInput"] input, [data-testid="stSelectbox"] > div,
[data-testid="stChatInput"] textarea {
    border-radius: 9px !important;
    border-color: var(--jr-border) !important;
}

[data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid var(--jr-border) !important;
    background: var(--jr-surface) !important;
    box-shadow: var(--jr-shadow-soft) !important;
}
</style>
"""
)


def injecter_theme() -> None:
    """Injecte le CSS partagé. À appeler une fois en haut de chaque page."""
    st.markdown(_CSS, unsafe_allow_html=True)


# def entete_plateforme(etiquette: str) -> None:
#     """En-tête de plateforme sobre : nom + étiquette de module courant."""
#     st.markdown(
#         f"""
#         <div class="jr-masthead">
#             <div class="jr-masthead__title">MyLegal Assist — Préparation de dossier</div>
#             <div class="jr-masthead__tag">{etiquette}</div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


from pathlib import Path
import base64

# Chemin vers le logo (à placer dans frontend/assets/logo_mylegal.png)
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo_mylegal.png"


# def entete_plateforme(etiquette: str) -> None:
#     """En-tête de plateforme : logo à gauche, nom + étiquette à droite."""
    
#     # Construction du HTML
#     html = '<div class="jr-masthead" style="display: flex; align-items: center; justify-content: space-between;">'
    
#     # Partie gauche : logo + titre
#     html += '<div style="display: flex; align-items: center; gap: 0.8rem;">'
    
#     # Ajout du logo s'il existe
#     if LOGO_PATH.exists():
#         with open(LOGO_PATH, "rb") as f:
#             img_data = base64.b64encode(f.read()).decode()
#         html += f'<img src="data:image/png;base64,{img_data}" alt="MyLegal Assist" style="height: 45px; width: auto;" />'
#     else:
#         # Fallback si le logo n'existe pas
#         html += '<span style="font-size: 1.8rem;">⚖️</span>'
    
#     html += f'<span class="jr-masthead__title" style="font-size: 1.5rem;">MyLegal Assist — Préparation de dossier</span>'
#     html += '</div>'
    
#     # Partie droite : étiquette
#     html += f'<div class="jr-masthead__tag">{etiquette}</div>'
    
#     html += '</div>'
    
#     st.markdown(html, unsafe_allow_html=True)


from pathlib import Path
import base64

# Chemin vers le logo
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo_mylegal.png"


def entete_plateforme(etiquette: str) -> None:
    """En-tête : logo en haut à gauche, titre centré, étiquette à droite."""
    
    # Construction du HTML
    html = '<div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">'
    
    # Gauche : LOGO (en haut à gauche)
    html += '<div style="display: flex; align-items: center;">'
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        html += f'<img src="data:image/png;base64,{img_data}" alt="MyLegal Assist" style="height: 50px; width: auto; margin-right: 10px;" />'
    else:
        html += '<span style="font-size: 2rem;">⚖️</span>'
    html += '</div>'
    
    # Centre : TITRE (centré)
    html += f'<div style="flex: 1; text-align: center;"><span style="font-family: Newsreader, serif; font-weight: 600; font-size: 1.5rem; color: var(--jr-ink);">MyLegal Assist — Préparation de dossier</span></div>'
    
    # Droite : ÉTIQUETTE
    html += f'<div><span class="jr-masthead__tag">{etiquette}</span></div>'
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

def note_pedagogique(texte: str) -> None:
    """Encart d'explication pédagogique, sobre, avant une section."""
    st.markdown(f'<div class="jr-note">{texte}</div>', unsafe_allow_html=True)


def badge(libelle: str, variante: str) -> str:
    """Retourne le HTML d'un badge sobre (pas d'emoji).

    variante : "success" | "warning" | "danger" | "neutral"
    """
    return f'<span class="jr-badge jr-badge--{variante}">{libelle}</span>'


def tag(texte: str) -> str:
    """Étiquette de référence façon tampon administratif (organisme, règle)."""
    return f'<span class="jr-tag">{texte}</span>'


