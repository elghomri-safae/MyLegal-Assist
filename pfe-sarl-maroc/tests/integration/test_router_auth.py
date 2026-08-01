"""Test d'intégration du routeur /auth, contre une base SQLite en mémoire réelle."""

from __future__ import annotations

from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import get_db
from backend.main import app
from backend.models import Base


def _client_avec_base_sqlite() -> TestClient:
    moteur = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(moteur)
    fabrique_session = sessionmaker(bind=moteur)

    def _remplacer_get_db() -> Generator[Session, None, None]:
        session = fabrique_session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _remplacer_get_db
    return TestClient(app)


def test_inscription_puis_connexion_reussies() -> None:
    """Un utilisateur inscrit doit pouvoir se connecter et obtenir un jeton."""
    client = _client_avec_base_sqlite()

    reponse_inscription = client.post(
        "/auth/inscription",
        json={
            "nom": "Alaoui",
            "email": "yasmine@example.com",
            "mot_de_passe": "SuperSecret123",
            "role": "entrepreneur",
        },
    )
    assert reponse_inscription.status_code == 201
    assert reponse_inscription.json()["role"] == "entrepreneur"

    reponse_connexion = client.post(
        "/auth/connexion",
        json={"email": "yasmine@example.com", "mot_de_passe": "SuperSecret123"},
    )

    app.dependency_overrides.pop(get_db, None)

    assert reponse_connexion.status_code == 200
    assert "access_token" in reponse_connexion.json()


def test_inscription_email_deja_utilise_retourne_409() -> None:
    """Une seconde inscription avec le même email doit être refusée (409)."""
    client = _client_avec_base_sqlite()
    payload = {
        "nom": "Test",
        "email": "double@example.com",
        "mot_de_passe": "abc12345",
        "role": "entrepreneur",
    }
    client.post("/auth/inscription", json=payload)
    reponse = client.post("/auth/inscription", json=payload)

    app.dependency_overrides.pop(get_db, None)

    assert reponse.status_code == 409


def test_inscription_email_deja_utilise_est_detectee_malgre_une_casse_differente() -> None:
    """L'unicité de l'email doit être vérifiée indépendamment de la casse."""
    client = _client_avec_base_sqlite()
    client.post(
        "/auth/inscription",
        json={
            "nom": "Test",
            "email": "Casse@Example.com",
            "mot_de_passe": "abc12345",
            "role": "entrepreneur",
        },
    )
    reponse = client.post(
        "/auth/inscription",
        json={
            "nom": "Autre",
            "email": "casse@example.com",
            "mot_de_passe": "autre12345",
            "role": "entrepreneur",
        },
    )

    app.dependency_overrides.pop(get_db, None)

    assert reponse.status_code == 409


def test_connexion_avec_une_casse_differente_de_l_inscription_reussit() -> None:
    """Un utilisateur doit pouvoir se connecter même avec une casse d'email différente."""
    client = _client_avec_base_sqlite()
    client.post(
        "/auth/inscription",
        json={
            "nom": "Test",
            "email": "MonEmail@Example.com",
            "mot_de_passe": "SuperSecret123",
            "role": "entrepreneur",
        },
    )
    reponse = client.post(
        "/auth/connexion",
        json={"email": "monemail@example.com", "mot_de_passe": "SuperSecret123"},
    )

    app.dependency_overrides.pop(get_db, None)

    assert reponse.status_code == 200
    assert "access_token" in reponse.json()


def test_connexion_mot_de_passe_incorrect_retourne_401() -> None:
    """Une connexion avec un mauvais mot de passe doit être refusée (401)."""
    client = _client_avec_base_sqlite()
    client.post(
        "/auth/inscription",
        json={
            "nom": "Test",
            "email": "x@example.com",
            "mot_de_passe": "abc12345",
            "role": "entrepreneur",
        },
    )

    reponse = client.post(
        "/auth/connexion", json={"email": "x@example.com", "mot_de_passe": "mauvais"}
    )

    app.dependency_overrides.pop(get_db, None)

    assert reponse.status_code == 401
