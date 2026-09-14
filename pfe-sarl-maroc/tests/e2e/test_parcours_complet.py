"""Test end-to-end : parcours complets « inscription -> connexion -> usage ».

Ces tests exercent l'assemblage réel du cycle de vie du dossier persistant
à travers l'authentification (Phase 6), via de vrais appels HTTP successifs
et une base SQLite en mémoire réelle (pas de mock sur la couche auth/rôles).
Le module système expert (`/dossiers/{id}/evaluer`) est utilisé comme module
de bout en bout car il ne nécessite aucune dépendance lourde externe
(contrairement à `/chat`, dont les dépendances lourdes restent testées
séparément avec des adaptateurs factices — voir tests/integration/).
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import get_db
from backend.main import app
from backend.models import Base


def _nouveau_client_e2e() -> TestClient:
    """Construit un TestClient avec une base SQLite en mémoire dédiée à ce test."""
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


def _inscrire_et_connecter(client: TestClient, email: str, role: str) -> str:
    """Inscrit un utilisateur puis se connecte, retourne le jeton d'accès."""
    client.post(
        "/auth/inscription",
        json={
            "nom": "Utilisateur Test",
            "email": email,
            "mot_de_passe": "MotDePasse123",
            "role": role,
        },
    )
    reponse = client.post("/auth/connexion", json={"email": email, "mot_de_passe": "MotDePasse123"})
    assert reponse.status_code == 200
    return reponse.json()["access_token"]


def test_parcours_entrepreneur_creation_remplissage_evaluation_dossier() -> None:
    """Un entrepreneur inscrit doit pouvoir créer un dossier, le compléter et
    l'évaluer comme conforme (CONCEPTION_V2.md §2, parcours utilisateur cible)."""
    client = _nouveau_client_e2e()
    jeton = _inscrire_et_connecter(client, "entrepreneur@example.com", "entrepreneur")
    en_tete = {"Authorization": f"Bearer {jeton}"}

    reponse = client.post(
        "/dossiers",
        json={
            "nom_projet": "Cabinet de conseil",
            "forme_juridique": "SARL AU",
            "capital_social": 50000,
            "siege_social": "12 rue des Fleurs, Casablanca",
        },
        headers=en_tete,
    )
    assert reponse.status_code == 201
    dossier_id = reponse.json()["id"]

    reponse = client.patch(
        f"/dossiers/{dossier_id}",
        json={
            "statuts_fournis": True,
            "certificat_negatif_fourni": True,
            "certificat_negatif_date_delivrance": "2026-07-15",
            "attestation_blocage_bancaire_fournie": False,
            "taxe_professionnelle_declaree": True,
            "affiliation_cnss_fournie": False,
        },
        headers=en_tete,
    )
    assert reponse.status_code == 200

    reponse = client.post(
        f"/dossiers/{dossier_id}/identites",
        json={
            "nom": "Alaoui",
            "prenom": "Yasmine",
            "numero_cin": "BE123456",
            "date_naissance": "1990-05-14",
        },
        headers=en_tete,
    )
    assert reponse.status_code == 201

    reponse = client.post(f"/dossiers/{dossier_id}/evaluer", headers=en_tete)

    app.dependency_overrides.pop(get_db, None)

    assert reponse.status_code == 201
    assert reponse.json()["statut_global"] == "conforme"


def test_parcours_sans_jeton_est_refuse() -> None:
    """Le même appel sans jeton d'authentification doit être refusé (401)."""
    client = _nouveau_client_e2e()

    reponse = client.post(
        "/dossiers", json={"nom_projet": "X", "forme_juridique": "SARL", "capital_social": 1}
    )

    app.dependency_overrides.pop(get_db, None)

    assert reponse.status_code == 401


def test_parcours_isolation_entre_utilisateurs() -> None:
    """Un entrepreneur ne doit jamais pouvoir accéder au dossier d'un autre
    (CONCEPTION_V2.md §3 : rôle Juriste supprimé, plus d'accès transverse)."""
    client = _nouveau_client_e2e()

    jeton_a = _inscrire_et_connecter(client, "a@example.com", "entrepreneur")
    reponse = client.post(
        "/dossiers",
        json={
            "nom_projet": "Projet A",
            "forme_juridique": "SARL AU",
            "capital_social": 10000,
            "siege_social": "Rabat",
        },
        headers={"Authorization": f"Bearer {jeton_a}"},
    )
    dossier_id = reponse.json()["id"]

    jeton_b = _inscrire_et_connecter(client, "b@example.com", "entrepreneur")
    reponse_croisee = client.get(
        f"/dossiers/{dossier_id}", headers={"Authorization": f"Bearer {jeton_b}"}
    )

    app.dependency_overrides.pop(get_db, None)

    assert reponse_croisee.status_code == 404


def test_route_regles_n_existe_plus() -> None:
    """Le catalogue de règles n'est plus exposé (CONCEPTION_V2.md §6.4, acté)."""
    client = _nouveau_client_e2e()
    jeton = _inscrire_et_connecter(client, "c@example.com", "entrepreneur")

    reponse = client.get("/regles", headers={"Authorization": f"Bearer {jeton}"})

    app.dependency_overrides.pop(get_db, None)

    assert reponse.status_code == 404
