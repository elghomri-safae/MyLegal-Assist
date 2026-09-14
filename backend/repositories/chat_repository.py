"""Accès aux données pour l'historique des conversations du chatbot."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.models.chat import CitationSource, Question, Reponse
from backend.rag.corpus_loader import DOCUMENTS_CONNUS
from backend.schemas.chat import ReponseChatbot


class ChatRepository:
    """Repository SQLAlchemy pour les questions/réponses persistées."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def creer_question(
        self, utilisateur_id: uuid.UUID, texte: str, dossier_id: uuid.UUID | None
    ) -> Question:
        question = Question(utilisateur_id=utilisateur_id, texte=texte, dossier_id=dossier_id)
        self._db.add(question)
        self._db.commit()
        self._db.refresh(question)
        return question

    def creer_reponse(self, question_id: uuid.UUID, reponse: ReponseChatbot) -> Reponse:
        """Persiste la réponse et ses citations. Valide que chaque citation
        pointe vers un document du corpus fermé (DOCUMENTS_CONNUS) — en
        l'absence d'une clé étrangère fiable (les tables SQL du corpus ne
        sont jamais peuplées, le corpus réel vit dans ChromaDB), c'est
        cette vérification applicative qui joue le rôle d'une FK."""
        entite = Reponse(question_id=question_id, texte=reponse.texte)
        for citation in reponse.citations:
            if citation.document not in DOCUMENTS_CONNUS:
                raise ValueError(
                    f"Citation vers un document hors corpus fermé : {citation.document!r}"
                )
            entite.citations.append(
                CitationSource(
                    document=citation.document,
                    niveau=citation.niveau,
                    article=citation.article,
                    page=citation.page,
                    provenance=citation.provenance,
                    reference=citation.reference,
                )
            )
        self._db.add(entite)
        self._db.commit()
        self._db.refresh(entite)
        return entite