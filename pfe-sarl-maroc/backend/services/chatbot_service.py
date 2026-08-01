"""Orchestration du chatbot compagnon du dossier (CONCEPTION_V2.md §6).

Principe directeur (§6.1) : le système expert reste l'unique source de
vérité sur l'état du dossier. Ce service ne modifie ni le moteur de règles
(backend.services.expert_service) ni le pipeline RAG
(backend.services.rag_service, backend.rag.*) — il les orchestre.

Séquence (§6.2) :
1. Contexte dossier chargé en premier (dernière évaluation + anomalies),
   si ``dossier_id`` est fourni.
2. Question factuelle sur l'état du dossier -> réponse construite
   directement depuis les anomalies, sans appel LLM ni RAG.
3. Question explicative (mots-clés : pourquoi/explique/comment/corriger)
   -> RAG + LLM, avec le contexte des anomalies injecté dans la question
   envoyée au pipeline existant (aucune modification de ce pipeline).
4. Question générale (pas de dossier_id) -> comportement RAG inchangé.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import DossierIntrouvableError
from backend.rag.embeddings import ModeleEmbedding
from backend.rag.generation import ClientLLM
from backend.rag.indexing import IndexVectoriel
from backend.rag.lexical_search import IndexLexicalBM25
from backend.repositories.chat_repository import ChatRepository
from backend.repositories.dossier_repository import DossierRepository
from backend.repositories.evaluation_repository import EvaluationRepository
from backend.schemas.chat import QuestionInput, ReponseChatbot
from backend.services.rag_service import repondre_question

_MOTS_CLES_EXPLICATIFS = (
    "pourquoi",
    "explique",
    "expliquer",
    "comment corriger",
    "comment faire",
    "comment resoudre",
    "comment régler",
)

_MESSAGE_DOSSIER_JAMAIS_EVALUE = (
    "Ce dossier n'a pas encore été évalué : aucune anomalie connue pour "
    "l'instant. Lancez une évaluation pour que je puisse vous dire précisément "
    "où il en est."
)


def _est_question_explicative(texte: str) -> bool:
    texte_normalise = texte.lower()
    return any(mot_cle in texte_normalise for mot_cle in _MOTS_CLES_EXPLICATIFS)


def _formater_contexte_anomalies(anomalies: list) -> str:
    if not anomalies:
        return "Ce dossier n'a, à ce jour, déclenché aucune anomalie."
    lignes = [
        f"- [{a.gravite}] {a.message} (règle {a.regle_id}, source : "
        f"{a.reference_documentaire}, niveau {a.niveau_documentaire})"
        for a in anomalies
    ]
    return "Anomalies de la dernière évaluation de ce dossier :\n" + "\n".join(lignes)


def _reponse_factuelle(anomalies: list) -> ReponseChatbot:
    """Réponse déterministe, sans LLM ni RAG (§6.2, étape 2) : l'état du
    dossier est déjà connu avec certitude via le système expert, aucune
    génération n'est nécessaire ni souhaitable.
    """
    if not anomalies:
        texte = "Aucune anomalie détectée lors de la dernière évaluation de ce dossier."
    else:
        bloquantes = [a for a in anomalies if a.gravite == "bloquante"]
        autres = [a for a in anomalies if a.gravite != "bloquante"]
        parties = []
        if bloquantes:
            parties.append(
                "Points bloquants à corriger avant dépôt :\n"
                + "\n".join(f"- {a.message}" for a in bloquantes)
            )
        if autres:
            parties.append(
                "Autres points signalés :\n" + "\n".join(f"- {a.message}" for a in autres)
            )
        texte = "\n\n".join(parties)
    return ReponseChatbot(texte=texte, citations=[])


def poser_question(
    db: Session,
    utilisateur_id: uuid.UUID,
    payload: QuestionInput,
    index_semantique: IndexVectoriel,
    index_lexical: IndexLexicalBM25,
    client_llm: ClientLLM,
    modele_embedding: ModeleEmbedding,
) -> ReponseChatbot:
    dossier_id = uuid.UUID(payload.dossier_id) if payload.dossier_id else None

    if dossier_id is None:
        # Étape 4 (§6.2) : question générale, comportement RAG inchangé.
        reponse = repondre_question(
            payload.texte, index_semantique, index_lexical, client_llm, modele_embedding
        )
    else:
        dossier = DossierRepository(db).obtenir(dossier_id, utilisateur_id)
        if dossier is None:
            raise DossierIntrouvableError("Dossier introuvable.")

        derniere_evaluation = EvaluationRepository(db).derniere_pour_dossier(dossier_id)

        if derniere_evaluation is None:
            # Rien à charger depuis le systeme expert : aucune évaluation
            # n'a encore eu lieu, on ne peut ni répondre factuellement ni
            # expliquer une anomalie qui n'existe pas.
            reponse = ReponseChatbot(texte=_MESSAGE_DOSSIER_JAMAIS_EVALUE, citations=[])
        elif not _est_question_explicative(payload.texte):
            # Étape 2 (§6.2) : réponse factuelle directe depuis les
            # anomalies de la dernière évaluation, sans appel LLM ni RAG.
            reponse = _reponse_factuelle(list(derniere_evaluation.anomalies))
        else:
            # Étape 3 (§6.2) : question explicative, RAG + LLM avec le
            # contexte des anomalies injecté dans la question — le pipeline
            # RAG lui-même (backend.services.rag_service, backend.rag.*)
            # n'est pas modifié.
            contexte = _formater_contexte_anomalies(list(derniere_evaluation.anomalies))
            question_augmentee = (
                f"{contexte}\n\nQuestion de l'utilisateur sur ce dossier : {payload.texte}"
            )
            reponse = repondre_question(
                question_augmentee, index_semantique, index_lexical, client_llm, modele_embedding
            )

    question = ChatRepository(db).creer_question(utilisateur_id, payload.texte, dossier_id)
    ChatRepository(db).creer_reponse(question.id, reponse)

    return reponse
