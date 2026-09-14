"""Génère les figures du rapport final (Phase 7) en PNG via matplotlib.

Ces figures reprennent fidèlement le contenu déjà validé dans docs/UML.md
(Phase 1) et ARCHITECTURE.md, simplement rendues en image statique plutôt
qu'en Mermaid, pour insertion dans le document Word du rapport.
"""

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

plt.rcParams["font.family"] = "DejaVu Sans"

OUT = "/home/claude/pfe-sarl-maroc/docs/rapport/figures"


def boite(ax, x, y, w, h, texte, fc="#EAF2FB", ec="#2C4A6E", fontsize=10, weight="normal"):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2, edgecolor=ec, facecolor=fc, mutation_aspect=1,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=fontsize,
             weight=weight, wrap=True)
    return rect


def fleche(ax, x1, y1, x2, y2, style="-|>", color="#333333", lw=1.3, ls="solid"):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, color=color,
                             linewidth=lw, linestyle=ls, mutation_scale=14)
    ax.add_patch(arrow)


def nouvelle_figure(w=12, h=8):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


# ---------------------------------------------------------------------------
# Figure 3.1 - Diagramme de cas d'utilisation
# ---------------------------------------------------------------------------
fig, ax = nouvelle_figure(12, 8)

# Acteurs
ax.text(0.8, 6.3, "Entrepreneur", ha="center", fontsize=10, weight="bold")
ax.text(0.8, 3.8, "Juriste", ha="center", fontsize=10, weight="bold")
ax.text(0.8, 1.3, "Admin", ha="center", fontsize=10, weight="bold")
for cy in (6.0, 3.5, 1.0):
    ax.add_patch(mpatches.Circle((0.8, cy - 0.35), 0.18, fc="#333", ec="#333"))
    ax.plot([0.8, 0.8], [cy - 0.55, cy - 1.0], color="#333", lw=1.3)
    ax.plot([0.55, 1.05], [cy - 0.75, cy - 0.75], color="#333", lw=1.3)
    ax.plot([0.8, 0.55], [cy - 1.0, cy - 1.35], color="#333", lw=1.3)
    ax.plot([0.8, 1.05], [cy - 1.0, cy - 1.35], color="#333", lw=1.3)

# Frontiere systeme
frontiere = mpatches.FancyBboxPatch((2.6, 0.3), 9.0, 7.2, boxstyle="round,pad=0.02",
                                     linewidth=1.4, edgecolor="#2C4A6E", facecolor="none")
ax.add_patch(frontiere)
ax.text(2.9, 7.2, "Système d'accompagnement création SARL", fontsize=10, weight="bold")

uc = [
    ("Poser une question\njuridique", 4.4, 6.4),
    ("Extraire données CIN\n(OCR)", 8.6, 6.4),
    ("Soumettre un dossier\nde création", 4.4, 4.7),
    ("Consulter le verdict\nde conformité", 8.6, 4.7),
    ("Consulter le catalogue\nde règles", 4.4, 3.0),
    ("Consulter l'historique\ndes évaluations", 8.6, 3.0),
    ("Superviser l'état\ndu système", 4.4, 1.3),
    ("Consulter les journaux\nd'erreurs", 8.6, 1.3),
]
for texte, cx, cy in uc:
    e = mpatches.Ellipse((cx, cy), 3.0, 1.15, fc="#EAF2FB", ec="#2C4A6E", lw=1.2)
    ax.add_patch(e)
    ax.text(cx, cy, texte, ha="center", va="center", fontsize=8.5)

liens = [
    (0.8, 6.0, 4.4, 6.7), (0.8, 6.0, 8.6, 6.7), (0.8, 6.0, 4.4, 5.0), (0.8, 6.0, 8.6, 5.0),
    (0.8, 3.5, 4.4, 3.3), (0.8, 3.5, 8.6, 3.3), (0.8, 3.5, 8.6, 1.6),
    (0.8, 1.0, 4.4, 1.6), (0.8, 1.0, 8.6, 1.6),
]
for x1, y1, x2, y2 in liens:
    ax.plot([x1, x2], [y1, y2], color="#888", lw=0.9, zorder=0)

ax.plot([4.4, 8.6], [4.15, 4.15], color="#888", lw=0.9, linestyle="--")
ax.text(6.5, 4.25, "«include»", fontsize=7.5, style="italic", ha="center")

fig.suptitle("Figure 3.1 — Diagramme de cas d'utilisation", fontsize=11, y=0.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_3_1_cas_utilisation.png", dpi=180, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3.2 - Diagramme de classes (simplifie)
# ---------------------------------------------------------------------------
fig, ax = nouvelle_figure(13, 8.5)

classes = {
    "Utilisateur": (0.5, 6.3, 2.8, 1.4, "+id\n+nom, email\n+role"),
    "Dossier": (4.2, 6.3, 2.8, 1.4, "+id\n+forme_juridique\n+capital_social\n+statut"),
    "IdentitePersonne": (8.0, 6.3, 3.1, 1.4, "+nom, prenom\n+numero_cin\n+source_extraction"),
    "Regle": (11.4, 6.3, 2.6, 1.4, "+id, categorie\n+gravite, niveau"),
    "PieceJustificative": (4.2, 4.2, 2.8, 1.2, "+type_piece\n+fournie"),
    "EvaluationDossier": (0.5, 4.2, 2.8, 1.2, "+date_evaluation\n+statut_global"),
    "Anomalie": (0.5, 2.1, 2.8, 1.2, "+message\n+gravite"),
    "Question": (8.0, 4.2, 2.6, 1.0, "+texte, date"),
    "Reponse": (11.0, 4.2, 2.6, 1.0, "+texte"),
    "CitationSource": (11.0, 2.4, 2.6, 1.0, "+document, niveau"),
    "DocumentCorpus": (8.0, 2.4, 2.6, 1.0, "+titre, niveau"),
    "Chunk": (4.2, 2.1, 2.6, 1.0, "+texte\n+embedding_ref"),
}
for nom, (x, y, w, h, attrs) in classes.items():
    boite(ax, x, y, w, h, f"{nom}\n—\n{attrs}", fontsize=8, weight="bold")

liens = [
    (1.9, 6.3, 1.9, 5.4, "1..*"), (5.6, 6.3, 1.9, 5.4, ""), (5.6, 6.3, 8.0, 6.6, "1..*"),
    (5.6, 6.3, 4.2, 4.8, "1..*"), (5.6, 6.3, 1.9, 5.4, ""), (1.9, 4.2, 1.9, 3.3, "0..*"),
    (9.3, 6.3, 9.3, 5.2, "1"), (12.3, 5.2, 11.4, 6.3, "1"),
    (9.3, 4.2, 12.3, 4.2, "1"), (12.3, 4.2, 12.3, 3.4, "1..*"),
    (9.3, 4.2, 9.3, 3.4, "1..*"),
]
fleche(ax, 1.9, 6.3, 1.9, 5.4)
fleche(ax, 5.6, 6.3, 5.6, 5.4)
fleche(ax, 7.0, 6.5, 8.0, 6.5)
fleche(ax, 5.6, 6.5, 4.6, 6.3)
fleche(ax, 1.9, 4.2, 1.9, 3.3)
fleche(ax, 9.3, 4.2, 9.3, 3.4)
fleche(ax, 12.3, 4.2, 12.3, 3.4)
fleche(ax, 11.0, 4.7, 9.3, 4.7)
fleche(ax, 5.6, 4.8, 5.6, 4.2)
fleche(ax, 2.9, 4.8, 4.2, 4.8)
fleche(ax, 12.7, 6.3, 2.9, 3.0)

ax.text(2.0, 5.55, "1..*", fontsize=7.5)
ax.text(5.7, 5.55, "0..*", fontsize=7.5)
ax.text(9.4, 3.55, "0..*", fontsize=7.5)

fig.suptitle("Figure 3.2 — Diagramme de classes (simplifié)", fontsize=11, y=0.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_3_2_classes.png", dpi=180, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3.3 - Diagramme de sequence : soumission de dossier
# ---------------------------------------------------------------------------
fig, ax = nouvelle_figure(12, 7)
acteurs = ["Entrepreneur", "Streamlit", "FastAPI\n(routeur dossier)", "expert_service", "rules/*.py"]
xs = [1.0, 3.5, 6.2, 9.0, 11.3]
for x, nom in zip(xs, acteurs):
    boite(ax, x - 0.9, 6.0, 1.8, 0.7, nom, fontsize=8.5, weight="bold")
    ax.plot([x, x], [6.0, 0.4], color="#999", lw=1, linestyle="--")

messages = [
    (1.0, 3.5, 5.3, "Remplit le formulaire"),
    (3.5, 6.2, 4.8, "POST /dossier/evaluer"),
    (6.2, 9.0, 4.3, "evaluer_dossier(donnees)"),
    (9.0, 11.3, 3.8, "charger_regles_applicables()"),
    (11.3, 9.0, 3.4, "liste de règles"),
    (9.0, 9.0, 3.0, "boucle : évaluer chaque règle"),
    (9.0, 6.2, 2.2, "verdict {statut, anomalies}"),
    (6.2, 3.5, 1.7, "200 OK {verdict}"),
    (3.5, 1.0, 1.2, "Affiche le verdict"),
]
for x1, x2, y, texte in messages:
    fleche(ax, x1, y, x2, y, lw=1.1)
    ax.text((x1 + x2) / 2, y + 0.15, texte, ha="center", fontsize=7.5)

fig.suptitle("Figure 3.3 — Diagramme de séquence : évaluation d'un dossier", fontsize=11, y=0.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_3_3_sequence_dossier.png", dpi=180, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3.4 - Modele de donnees (ERD simplifie)
# ---------------------------------------------------------------------------
fig, ax = nouvelle_figure(13, 7.5)
tables = {
    "utilisateurs": (0.5, 5.7, 2.6, "id, nom, email,\nrole, mdp_hash"),
    "dossiers": (4.0, 5.7, 2.6, "id, entrepreneur_id,\nforme_juridique, capital"),
    "identites_personnes": (7.5, 5.7, 2.9, "id, dossier_id,\nnom, cin, naissance"),
    "pieces_justificatives": (11.0, 5.7, 2.0, "id, dossier_id,\ntype, fournie"),
    "regles": (0.5, 3.6, 2.6, "id, categorie,\ngravite, niveau"),
    "evaluations_dossier": (4.0, 3.6, 2.6, "id, dossier_id,\nstatut_global"),
    "anomalies": (7.5, 3.6, 2.6, "id, evaluation_id,\nregle_id, message"),
    "questions": (0.5, 1.6, 2.4, "id, utilisateur_id,\ntexte, date"),
    "reponses": (3.4, 1.6, 2.2, "id, question_id,\ntexte"),
    "citations_sources": (6.1, 1.6, 2.6, "id, reponse_id,\ndocument, niveau"),
    "documents_corpus": (9.2, 1.6, 2.3, "id, titre, niveau"),
    "chunks": (11.9, 3.6, 1.8, "id, document_id,\ntexte"),
}
for nom, (x, y, w, extra) in tables.items():
    boite(ax, x, y, w, 1.35, f"{nom}\n—\n{extra}", fontsize=7.5, weight="bold", fc="#F3F0FA")

fig.suptitle("Figure 3.4 — Modèle de données (ERD simplifié)", fontsize=11, y=0.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_3_4_erd.png", dpi=180, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4.1 - Architecture globale (3 modules + integration)
# ---------------------------------------------------------------------------
fig, ax = nouvelle_figure(13, 8)
boite(ax, 5.0, 6.7, 3.0, 1.0, "Streamlit\n(5 pages)", fc="#FDEEDC")
boite(ax, 5.0, 5.1, 3.0, 1.0, "FastAPI\nauth + rôles (JWT)", fc="#EAF2FB")

boite(ax, 0.5, 3.0, 3.4, 1.3, "Système expert\nanti-rejet\n(rules/*, expert_service)", fc="#E7F5EC")
boite(ax, 4.8, 3.0, 3.4, 1.3, "OCR CIN\n(ocr/*, ocr_service)\nEasyOCR + OpenCV", fc="#E7F5EC")
boite(ax, 9.1, 3.0, 3.4, 1.3, "RAG juridique\n(rag/*, rag_service)\nChromaDB + Groq", fc="#E7F5EC")

boite(ax, 0.5, 0.7, 3.4, 1.3, "PostgreSQL\n(utilisateurs, dossiers,\nrègles, historique)", fc="#F3F0FA")
boite(ax, 4.8, 0.7, 3.4, 1.3, "data/raw, chunks,\nembeddings\n(corpus fermé S1-S6)", fc="#F3F0FA")
boite(ax, 9.1, 0.7, 3.4, 1.3, "ChromaDB\n(index vectoriel)", fc="#F3F0FA")

for x in (6.5, 6.5):
    fleche(ax, 6.5, 6.7, 6.5, 6.1)
fleche(ax, 6.5, 5.1, 2.2, 4.3)
fleche(ax, 6.5, 5.1, 6.5, 4.3)
fleche(ax, 6.5, 5.1, 10.8, 4.3)
fleche(ax, 2.2, 3.0, 2.2, 2.0)
fleche(ax, 6.5, 3.0, 6.5, 2.0)
fleche(ax, 10.8, 3.0, 10.8, 2.0)

fig.suptitle("Figure 4.1 — Architecture globale du système", fontsize=11, y=0.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_4_1_architecture.png", dpi=180, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 7.1 - Pipeline RAG complet
# ---------------------------------------------------------------------------
fig, ax = nouvelle_figure(13, 4.2)
etapes_haut = ["data/raw\n(corpus fermé)", "extraction.py", "cleaning.py", "chunking.py\n(LangChain)", "embeddings.py\n(sentence-transf.)", "indexing.py\n(ChromaDB)"]
etapes_bas = ["Question", "embeddings.py", "recherche\nsémantique + BM25", "hybrid_search.py\n(fusion RRF)", "reranking.py\n(niveau doc.)", "generation.py\n(Groq + citations)"]

for i, texte in enumerate(etapes_haut):
    boite(ax, 0.3 + i * 2.1, 2.6, 1.9, 1.1, texte, fontsize=7.5, fc="#EAF2FB")
    if i > 0:
        fleche(ax, 0.3 + i * 2.1 - 0.2, 3.15, 0.3 + i * 2.1, 3.15)

for i, texte in enumerate(etapes_bas):
    boite(ax, 0.3 + i * 2.1, 0.3, 1.9, 1.1, texte, fontsize=7.5, fc="#E7F5EC")
    if i > 0:
        fleche(ax, 0.3 + i * 2.1 - 0.2, 0.85, 0.3 + i * 2.1, 0.85)

ax.text(0.1, 3.85, "Indexation (offline, scripts/indexer_corpus.py)", fontsize=8.5, weight="bold")
ax.text(0.1, 1.55, "Requête (online, rag_service.py, à chaque question)", fontsize=8.5, weight="bold")

fig.suptitle("Figure 7.1 — Pipeline RAG complet (indexation et requête)", fontsize=11, y=0.02)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_7_1_pipeline_rag.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Figures generees avec succes.")
