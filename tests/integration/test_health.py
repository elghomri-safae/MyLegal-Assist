"""Test d'integration du endpoint /health.

La dependance get_db est substituee par une session factice : ce test
valide le contrat HTTP du endpoint sans necessiter un serveur PostgreSQL
reel, ce qui reste possible et pertinent puisque la logique testee (routage,
serialisation de la reponse) ne depend pas du contenu de la base.
"""

from fastapi.testclient import TestClient

from backend.core.database import get_db
from backend.main import app


class _FakeSession:
    """Substitut minimal d'une session SQLAlchemy pour les tests."""

    def execute(self, _statement: object) -> None:
        """Simule l'execution reussie d'une requete SQL."""
        return None


def _override_get_db():
    yield _FakeSession()


client = TestClient(app)


def test_healthcheck_returns_ok() -> None:
    """Le endpoint /health doit signaler l'API et la base comme disponibles."""
    app.dependency_overrides[get_db] = _override_get_db
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
