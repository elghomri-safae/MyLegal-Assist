


"""Orchestration du chatbot compagnon du dossier (CONCEPTION_V2.md §6).

Principe directeur (§6.1) : le système expert reste l'unique source de
vérité sur l'état du dossier. Ce service ne modifie ni le moteur de règles
(backend.services.expert_service) ni le pipeline RAG
(backend.services.rag_service, backend.rag.*) — il les orchestre.

Séquence (§6.2) :
1. Contexte dossier chargé en premier (dernière évaluation + anomalies),
   si ``dossier_id`` est fourni.
2. Question de statut sur le dossier (mots-clés : statut/conforme/
   anomalie/avancement...) -> réponse construite directement depuis les
   anomalies, sans appel LLM ni RAG.
3. Toute autre question, dossier sélectionné ou non -> pipeline RAG avec
   la question brute (aucun contexte de dossier injecté), sous le même
   seuil de confiance strict (SEUIL_CONFIANCE_PAR_DEFAUT).

Cette architecture garantit qu'une question hors périmètre est rejetée
avec la même rigueur, qu'un dossier soit sélectionné ou non : un seul
seuil de confiance, calibré empiriquement (cf. rapport, section 4.3.3),
s'applique dans tous les cas où le pipeline RAG est sollicité.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import DossierIntrouvableError
from backend.rag.embeddings import ModeleEmbedding
from backend.rag.generation import ClientLLM
from backend.rag.indexing import IndexVectoriel
from backend.rag.lexical_search import IndexLexicalBM25
from backend.rag.reranking import ModeleReranker, SEUIL_CONFIANCE_PAR_DEFAUT
from backend.repositories.chat_repository import ChatRepository
from backend.repositories.dossier_repository import DossierRepository
from backend.repositories.evaluation_repository import EvaluationRepository
from backend.schemas.chat import QuestionInput, ReponseChatbot
from backend.services.rag_service import repondre_question

from backend.models.chat import Question
from backend.schemas.chat import CitationRead, QuestionHistoriqueRead


_MOTS_CLES_STATUT = (
    "statut",
    "état",
    "conforme",
    "conformité",
    "anomalie",
    "anomalies",
    "avancement",
    "où en est",
    "mon dossier",
)

_MESSAGE_DOSSIER_JAMAIS_EVALUE = (
    "Ce dossier n'a pas encore été évalué : aucune anomalie connue pour "
    "l'instant. Lancez une évaluation pour que je puisse vous dire précisément "
    "où il en est."
)


def _est_question_statut(texte: str) -> bool:
    """Détection positive d'une question sur le statut du dossier : ne
    déclenche la réponse factuelle que si un marqueur explicite est
    présent, plutôt que par défaut."""
    texte_normalise = texte.lower()
    return any(mot_cle in texte_normalise for mot_cle in _MOTS_CLES_STATUT)


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
        partes = []
        if bloquantes:
            partes.append(
                "Points bloquants à corriger avant dépôt :\n"
                + "\n".join(f"- {a.message}" for a in bloquantes)
            )
        if autres:
            partes.append(
                "Autres points signalés :\n" + "\n".join(f"- {a.message}" for a in autres)
            )
        texte = "\n\n".join(partes)
    return ReponseChatbot(texte=texte, citations=[])


def lister_historique(
    db: Session,
    utilisateur_id: uuid.UUID,
    dossier_id: uuid.UUID | None = None,
) -> list[QuestionHistoriqueRead]:
    """Historique des échanges du chatbot pour un utilisateur (Amélioration 5),
    trié par date décroissante. Filtre optionnel par dossier."""
    requete = db.query(Question).filter(Question.utilisateur_id == utilisateur_id)
    if dossier_id is not None:
        requete = requete.filter(Question.dossier_id == dossier_id)
    questions = requete.order_by(Question.date.desc()).all()

    resultats: list[QuestionHistoriqueRead] = []
    for q in questions:
        reponse = q.reponse
        resultats.append(
            QuestionHistoriqueRead(
                id=str(q.id),
                dossier_id=str(q.dossier_id) if q.dossier_id else None,
                texte=q.texte,
                date=q.date,
                reponse_texte=reponse.texte if reponse else None,
                citations=[
                    CitationRead(
                        id=str(c.id),
                        document=c.document,
                        niveau=c.niveau,
                        article=c.article,
                        page=c.page,
                        provenance=c.provenance,
                        reference=c.reference,
                    )
                    for c in (reponse.citations if reponse else [])
                ],
            )
        )
    return resultats


def poser_question(
    db: Session,
    utilisateur_id: uuid.UUID,
    payload: QuestionInput,
    index_semantique: IndexVectoriel,
    index_lexical: IndexLexicalBM25,
    client_llm: ClientLLM,
    modele_embedding: ModeleEmbedding,
    reranker_modele: ModeleReranker,
) -> ReponseChatbot:
    dossier_id = uuid.UUID(payload.dossier_id) if payload.dossier_id else None

    # Créer la question AVANT tout traitement, pour garantir que
    # l'historique soit conservé dans tous les cas.
    question = ChatRepository(db).creer_question(utilisateur_id, payload.texte, dossier_id)

    if dossier_id is None:
        # Question générale, aucun dossier sélectionné.
        reponse = repondre_question(
            payload.texte,
            index_semantique,
            index_lexical,
            client_llm,
            reranker_modele,
            modele_embedding,
        )
    else:
        dossier = DossierRepository(db).obtenir(dossier_id, utilisateur_id)
        if dossier is None:
            raise DossierIntrouvableError("Dossier introuvable.")

        derniere_evaluation = EvaluationRepository(db).derniere_pour_dossier(dossier_id)

        if derniere_evaluation is None:
            # Rien à charger depuis le systeme expert : aucune évaluation
            # n'a encore eu lieu, on ne peut pas répondre factuellement.
            reponse = ReponseChatbot(texte=_MESSAGE_DOSSIER_JAMAIS_EVALUE, citations=[])

        elif _est_question_statut(payload.texte):
            # Étape 2 (§6.2) : question de statut explicitement détectée
            # -> réponse factuelle directe depuis les anomalies de la
            # dernière évaluation, sans appel LLM ni RAG.
            reponse = _reponse_factuelle(list(derniere_evaluation.anomalies))

        else:
            # Étape 3 (§6.2) : toute autre question -> RAG avec la
            # question brute (aucun contexte d'anomalies injecté), sous
            # le même seuil de confiance strict que pour les questions
            # générales.
            reponse = repondre_question(
                payload.texte,
                index_semantique,
                index_lexical,
                client_llm,
                reranker_modele,
                modele_embedding,
                seuil_confiance=SEUIL_CONFIANCE_PAR_DEFAUT,
            )

    # Sauvegarder la réponse (la question existe maintenant)
    try:
        ChatRepository(db).creer_reponse(question.id, reponse)
    except ValueError:
        ChatRepository(db).creer_reponse(
            question.id,
            ReponseChatbot(
                texte="Une erreur est survenue lors de l'enregistrement de la réponse.",
                citations=[],
            ),
        )
    return reponse