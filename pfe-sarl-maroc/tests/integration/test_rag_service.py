"""Test d'intégration du pipeline RAG au moment de la requête (rag_service.py).

Les trois dépendances lourdes (modèle d'embedding, index vectoriel, client
LLM) sont substituées par des adaptateurs factices respectant les mêmes
interfaces (``ModeleEmbedding``, ``IndexVectoriel``, ``ClientLLM``), afin de
tester le pipeline de bout en bout (recherche hybride, reranking,
génération, citations) sans dépendre de sentence-transformers, ChromaDB ni
de l'API Groq (non exercés dans cet environnement de vérification — voir
ARCHITECTURE.md §12).
"""

from __future__ import annotations

from backend.rag.chunking import ChunkDocument
from backend.rag.indexing import ResultatRechercheSemantique
from backend.rag.lexical_search import IndexLexicalBM25
from backend.services.rag_service import MESSAGE_AUCUNE_SOURCE_PERTINENTE, repondre_question


class _ModeleEmbeddingFactice:
    def encoder(self, textes: list[str]) -> list[tuple[float, ...]]:
        return [(1.0, 0.0, 0.0) for _ in textes]


class _IndexSemantiqueFactice:
    def __init__(self, resultats: list[ResultatRechercheSemantique]) -> None:
        self._resultats = resultats

    def ajouter(self, chunks, vecteurs):  # noqa: ANN001 - non utilise dans ce test
        raise NotImplementedError

    def rechercher(self, vecteur_requete, k: int) -> list[ResultatRechercheSemantique]:
        return self._resultats[:k]


class _ClientLLMFactice:
    def __init__(self, texte: str) -> None:
        self._texte = texte

    def generer(self, prompt_systeme: str, prompt_utilisateur: str) -> str:
        return self._texte


def _chunk(document_titre: str, niveau: int, texte: str) -> ChunkDocument:
    return ChunkDocument(
        document_titre=document_titre, niveau=niveau, type_source="x", position=0, texte=texte
    )


def test_pipeline_complet_retourne_reponse_avec_citations() -> None:
    """Le pipeline complet doit retourner une réponse et des citations tracables."""
    chunk_pertinent = _chunk(
        "Loi 5-96", 1, "Le capital social minimum de la SARL est fixe librement par les associes."
    )
    index_semantique = _IndexSemantiqueFactice(
        [ResultatRechercheSemantique(identifiant="c0", chunk=chunk_pertinent, score=0.95)]
    )
    index_lexical = IndexLexicalBM25([chunk_pertinent])
    client_llm = _ClientLLMFactice("Le capital social est fixe librement [Loi 5-96, Niveau 1].")

    resultat = repondre_question(
        question="Quel est le capital minimum d'une SARL ?",
        index_semantique=index_semantique,
        index_lexical=index_lexical,
        client_llm=client_llm,
        modele_embedding=_ModeleEmbeddingFactice(),
    )

    assert "capital" in resultat.texte.lower()
    assert len(resultat.citations) == 1
    assert resultat.citations[0].document == "Loi 5-96"
    assert resultat.citations[0].niveau == 1


def test_pipeline_sans_resultat_pertinent_signale_l_absence_de_source() -> None:
    """Sans aucun résultat pertinent, le pipeline doit le signaler explicitement."""
    index_semantique = _IndexSemantiqueFactice([])
    index_lexical = IndexLexicalBM25([])
    client_llm = _ClientLLMFactice("Ne devrait pas etre appele.")

    resultat = repondre_question(
        question="Question sans rapport avec le corpus",
        index_semantique=index_semantique,
        index_lexical=index_lexical,
        client_llm=client_llm,
        modele_embedding=_ModeleEmbeddingFactice(),
    )

    assert resultat.texte == MESSAGE_AUCUNE_SOURCE_PERTINENTE
    assert resultat.citations == []
