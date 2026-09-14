
"""Schémas Pydantic du module chatbot juridique (RAG).

MODIFICATION (intégration corpus juridique) : ``CitationOutput`` reflétait
l'ancien format de citation (``document``, ``niveau`` obligatoire,
``reference``). Le pipeline RAG finalisé (``backend/rag/generation.py``)
produit désormais des ``Citation`` avec ``article``, ``page`` et
``provenance``, et ``niveau`` toujours à ``None`` (aucune hiérarchie
artificielle introduite, décision actée). ``niveau`` devient donc optionnel
(compat : un ancien client qui l'attendrait recevra ``null`` plutôt qu'une
erreur), et les nouveaux champs sont ajoutés.
"""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class QuestionInput(BaseModel):
    """Question posée par un utilisateur au chatbot juridique.

    ``dossier_id`` absent ou nul = question générale (RAG seul, comportement
    inchangé). Renseigné = question contextuelle à ce dossier précis
    (CONCEPTION_V2.md §6.2).
    """

    texte: str
    dossier_id: str | None = None


class CitationOutput(BaseModel):
    """Une citation associée à la réponse : document, article, page et
    provenance lorsqu'ils sont connus."""

    document: str
    niveau: int | None = None
    article: str | None = None
    page: int | None = None
    provenance: str
    reference: str


class ReponseChatbot(BaseModel):
    """Réponse du chatbot, avec ses citations."""

    texte: str
    citations: list[CitationOutput]

# une autre nouvelle fonction 
class CitationRead(BaseModel):
    """Une citation associée à une réponse, telle que consultable dans l'historique."""

    id: str
    document: str
    niveau: int | None
    article: str | None
    page: int | None
    provenance: str
    reference: str
    
class QuestionHistoriqueRead(BaseModel):
    """Un échange complet (question + réponse + citations), pour l'historique
    de conversation d'un utilisateur (Amélioration 5)."""

    id: str
    dossier_id: str | None
    texte: str
    date: datetime
    reponse_texte: str | None
    citations: list[CitationRead]
# 