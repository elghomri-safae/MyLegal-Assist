"""Service orchestrant le pipeline RAG au moment de la requête (question -> réponse).

Pipeline : embedding de la question (préfixe E5 "query: ") -> recherche
hybride (sémantique + lexicale, RRF) -> reranking neuronal
(BAAI/bge-reranker-v2-m3) -> filtre de confiance -> génération avec
citations (Groq).

reranker_score(question, resultats_fusionnes, reranker_modele)
 utilise un vrai modèle d'IA (cross-encoder). Ce modèle prend 
 la question ET un passage en entrée, et retourne un score 
 de 0 à 1 indiquant à quel point le passage répond à la question. 
 Pour fonctionner, il a obligatoirement besoin de la question.


- ``encoder_requete`` (préfixe E5 "query: ") remplace l'encodage brut ;
- ``reranker_score`` (nouvelle signature, avec la question) remplace
  ``reranker`` — et son score de confiance est exploité pour couper avant
  l'appel LLM si aucun passage n'est assez pertinent (seuil calibré
  empiriquement sur ce corpus, cf. ``rag_pipeline.py``) — ce filtre
  n'existait pas du tout ici auparavant : ``/chat`` appelait Groq pour
  n'importe quelle question hors périmètre ;
- les citations sont dédupliquées avant réponse (même référence répétée
  plusieurs fois sinon) ;
- ``CitationOutput`` inclut désormais ``article``, ``page`` et
  ``provenance`` (cf. ``backend/schemas/chat.py``).

L'indexation du corpus (extraction -> nettoyage -> chunking -> embeddings ->
indexation) est un pipeline distinct, exécuté hors-ligne via
``scripts/importer_corpus_structurel.py`` puis ``scripts/build_index.py``.
"""

from __future__ import annotations

from backend.rag.embeddings import ModeleEmbedding, encoder_requete, obtenir_modele_embedding
from backend.rag.generation import ClientLLM, deduppliquer_citations, generer_reponse
from backend.rag.hybrid_search import fusionner_resultats
from backend.rag.indexing import IndexVectoriel
from backend.rag.lexical_search import IndexLexicalBM25
from backend.rag.reranking import ModeleReranker, SEUIL_CONFIANCE_PAR_DEFAUT, reranker_score
from backend.schemas.chat import CitationOutput, ReponseChatbot

NB_RESULTATS_PAR_METHODE = 8
NB_EXTRAITS_RETENUS = 6

MESSAGE_AUCUNE_SOURCE_PERTINENTE = (
    "Le corpus documentaire disponible ne permet pas de repondre a cette question : "
    "aucune source pertinente n'a ete trouvee."
)


def repondre_question(
    question: str,
    index_semantique: IndexVectoriel,
    index_lexical: IndexLexicalBM25,
    client_llm: ClientLLM,
    reranker_modele: ModeleReranker,
    modele_embedding: ModeleEmbedding | None = None,
    seuil_confiance: float = SEUIL_CONFIANCE_PAR_DEFAUT,
) -> ReponseChatbot:
    """Exécute le pipeline RAG complet pour une question donnée.

    ``seuil_confiance`` : seuil de confiance du reranker (sigmoïde, [0, 1])
    en dessous duquel le pipeline renonce à générer une réponse. Une valeur
    plus basse (utilisée pour les questions posées dans le contexte d'un
    dossier) tolère un score dilué par le contexte des anomalies injecté,
    tout en continuant à filtrer les questions réellement hors périmètre.
    """
    modele_effectif = (
        modele_embedding if modele_embedding is not None else obtenir_modele_embedding()
    )

    vecteur_question = encoder_requete(question, modele_effectif)

    resultats_semantiques = index_semantique.rechercher(
        vecteur_question, k=NB_RESULTATS_PAR_METHODE
    )
    resultats_lexicaux = index_lexical.rechercher(question, k=NB_RESULTATS_PAR_METHODE)

    resultats_fusionnes = fusionner_resultats(resultats_semantiques, resultats_lexicaux)
    resultats_rerankes = reranker_score(question, resultats_fusionnes, reranker_modele)

    meilleur_score = resultats_rerankes[0].score if resultats_rerankes else 0.0
    seuil_franchi = meilleur_score < seuil_confiance
    if not resultats_rerankes or seuil_franchi:
        return ReponseChatbot(texte=MESSAGE_AUCUNE_SOURCE_PERTINENTE, citations=[])

    extraits = [item.resultat for item in resultats_rerankes[:NB_EXTRAITS_RETENUS]]
    reponse_generee = generer_reponse(question, extraits, client_llm)

    citations_dedupliquees = deduppliquer_citations(reponse_generee.citations)

    return ReponseChatbot(
        texte=reponse_generee.texte,
        citations=[
            CitationOutput(
                document=c.document,
                article=c.article,
                page=c.page,
                provenance=c.provenance,
                reference=c.reference,
            )
            for c in citations_dedupliquees
        ],
    )
