"""Test d'intégration du routeur /chat.

Les trois dépendances lourdes sont substituées via ``app.dependency_overrides``.
"""

from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import get_db
from backend.core.dependencies import UtilisateurConnecte, obtenir_utilisateur_connecte
from backend.main import app
from backend.models import Base
from backend.rag.chunking import ChunkDocument
from backend.rag.indexing import ResultatRechercheSemantique
from backend.rag.lexical_search import IndexLexicalBM25
from backend.routers.chat import (
    obtenir_client_llm,
    obtenir_index_lexical,
    obtenir_index_semantique,
    obtenir_modele_embedding_dependance,
)


def _remplacer_get_db() -> Generator[Session, None, None]:
    moteur = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(moteur)
    session = sessionmaker(bind=moteur)()
    try:
        yield session
    finally:
        session.close()


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
    def generer(self, prompt_systeme: str, prompt_utilisateur: str) -> str:
        return "Reponse de test [Loi 5-96, Niveau 1]."


def test_poser_question_retourne_une_reponse_avec_citations() -> None:
    """POST /chat doit retourner 200 avec une réponse et ses citations."""
    chunk = ChunkDocument(
        document_titre="Loi 5-96",
        niveau=1,
        type_source="texte_de_loi",
        position=0,
        texte="Le capital social minimum de la SARL est fixe librement.",
    )
    app.dependency_overrides[obtenir_index_semantique] = lambda: _IndexSemantiqueFactice(
        [ResultatRechercheSemantique(identifiant="c0", chunk=chunk, score=0.9)]
    )
    app.dependency_overrides[obtenir_index_lexical] = lambda: IndexLexicalBM25([chunk])
    app.dependency_overrides[obtenir_client_llm] = lambda: _ClientLLMFactice()
    app.dependency_overrides[obtenir_modele_embedding_dependance] = (
        lambda: _ModeleEmbeddingFactice()
    )
    app.dependency_overrides[obtenir_utilisateur_connecte] = lambda: UtilisateurConnecte(
        id="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee", email="test@example.com", role="entrepreneur"
    )
    app.dependency_overrides[get_db] = _remplacer_get_db

    client = TestClient(app)
    try:
        response = client.post("/chat", json={"texte": "Quel est le capital minimum ?"})
    finally:
        app.dependency_overrides.pop(obtenir_index_semantique, None)
        app.dependency_overrides.pop(obtenir_index_lexical, None)
        app.dependency_overrides.pop(obtenir_client_llm, None)
        app.dependency_overrides.pop(obtenir_modele_embedding_dependance, None)
        app.dependency_overrides.pop(obtenir_utilisateur_connecte, None)
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["texte"] == "Reponse de test [Loi 5-96, Niveau 1]."
    assert data["citations"][0]["document"] == "Loi 5-96"
