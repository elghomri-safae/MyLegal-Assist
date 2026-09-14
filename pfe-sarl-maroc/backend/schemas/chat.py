"""Schémas Pydantic du module chatbot juridique (RAG)."""

from __future__ import annotations

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
    """Une citation (source, niveau, référence) associée à la réponse."""

    document: str
    niveau: int
    reference: str


class ReponseChatbot(BaseModel):
    """Réponse du chatbot, avec ses citations."""

    texte: str
    citations: list[CitationOutput]
