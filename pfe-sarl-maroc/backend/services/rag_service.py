"""Service orchestrant le pipeline RAG au moment de la requête (question -> réponse).

Pipeline : embedding de la question -> recherche hybride (sémantique +
lexicale, RRF) -> reranking (priorité au niveau documentaire) -> génération
avec citations (Groq).

L'indexation du corpus (extraction -> nettoyage -> chunking -> embeddings ->
indexation) est un pipeline distinct, exécuté hors-ligne via
``scripts/indexer_corpus.py`` (voir ARCHITECTURE.md §12).
"""

from __future__ import annotations

from backend.rag.embeddings import ModeleEmbedding, obtenir_modele_embedding
from backend.rag.generation import ClientLLM, generer_reponse
from backend.rag.hybrid_search import fusionner_resultats
from backend.rag.indexing import IndexVectoriel
from backend.rag.lexical_search import IndexLexicalBM25
from backend.rag.reranking import reranker
from backend.schemas.chat import CitationOutput, ReponseChatbot

NB_RESULTATS_PAR_METHODE = 5
NB_EXTRAITS_RETENUS = 4

MESSAGE_AUCUNE_SOURCE_PERTINENTE = (
    "Le corpus documentaire disponible ne permet pas de repondre a cette question : "
    "aucune source pertinente n'a ete trouvee."
)


def repondre_question(
    question: str,
    index_semantique: IndexVectoriel,
    index_lexical: IndexLexicalBM25,
    client_llm: ClientLLM,
    modele_embedding: ModeleEmbedding | None = None,
) -> ReponseChatbot:
    """Exécute le pipeline RAG complet pour une question donnée."""
    modele_effectif = (
        modele_embedding if modele_embedding is not None else obtenir_modele_embedding()
    )

    vecteur_question = modele_effectif.encoder([question])[0]

    resultats_semantiques = index_semantique.rechercher(
        vecteur_question, k=NB_RESULTATS_PAR_METHODE
    )
    resultats_lexicaux = index_lexical.rechercher(question, k=NB_RESULTATS_PAR_METHODE)

    resultats_fusionnes = fusionner_resultats(resultats_semantiques, resultats_lexicaux)
    resultats_rerankes = reranker(resultats_fusionnes)[:NB_EXTRAITS_RETENUS]

    if not resultats_rerankes:
        return ReponseChatbot(texte=MESSAGE_AUCUNE_SOURCE_PERTINENTE, citations=[])

    reponse_generee = generer_reponse(question, resultats_rerankes, client_llm)

    return ReponseChatbot(
        texte=reponse_generee.texte,
        citations=[
            CitationOutput(document=c.document, niveau=c.niveau, reference=c.reference)
            for c in reponse_generee.citations
        ],
    )
