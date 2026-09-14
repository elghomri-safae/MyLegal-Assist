"""Test d'intégration du routeur /dossiers (cycle de vie persistant, CONCEPTION_V2.md §5)."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import get_db
from backend.core.dependencies import UtilisateurConnecte, obtenir_utilisateur_connecte
from backend.main import app
from backend.models import Base


@pytest.fixture(autouse=True)
def _nettoyer_dependency_overrides() -> Generator[None, None, None]:
    """Empêche la pollution d'état entre tests : sans ce nettoyage, une
    surcharge posée ici (get_db, obtenir_utilisateur_connecte) reste active
    pour tous les tests suivants du même processus pytest, quel que soit le
    fichier — bug déjà rencontré et corrigé une fois dans ce projet
    (voir DECISIONS.md, Phase 6).
    """
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(obtenir_utilisateur_connecte, None)


def _nouveau_client() -> TestClient:
    moteur = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
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
    app.dependency_overrides[obtenir_utilisateur_connecte] = lambda: UtilisateurConnecte(
        id="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee", email="test@example.com", role="entrepreneur"
    )
    return TestClient(app)


def _creer_dossier(client: TestClient, **kwargs: object) -> dict:
    payload = {
        "nom_projet": "Mon projet",
        "forme_juridique": "SARL AU",
        "capital_social": 50000,
        "siege_social": "12 rue des Fleurs, Casablanca",
    }
    payload.update(kwargs)
    reponse = client.post("/dossiers", json=payload)
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def test_evaluer_dossier_valide_retourne_conforme() -> None:
    """Un dossier complet et cohérent doit être évalué comme conforme."""
    client = _nouveau_client()
    dossier = _creer_dossier(client)

    client.patch(
        f"/dossiers/{dossier['id']}",
        json={
            "statuts_fournis": True,
            "certificat_negatif_fourni": True,
            "certificat_negatif_date_delivrance": "2026-07-15",
            "attestation_blocage_bancaire_fournie": False,
            "taxe_professionnelle_declaree": True,
            "affiliation_cnss_fournie": False,
        },
    )
    client.post(
        f"/dossiers/{dossier['id']}/identites",
        json={
            "nom": "Alaoui",
            "prenom": "Yasmine",
            "numero_cin": "BE123456",
            "date_naissance": "1990-05-14",
        },
    )

    reponse = client.post(f"/dossiers/{dossier['id']}/evaluer")
    assert reponse.status_code == 201
    assert reponse.json()["statut_global"] == "conforme"


def test_creer_dossier_capital_negatif_est_rejete_par_validation() -> None:
    """Un capital social négatif ou nul doit être rejeté au niveau du schéma (422)."""
    client = _nouveau_client()
    reponse = client.post(
        "/dossiers",
        json={
            "nom_projet": "Mon projet",
            "forme_juridique": "SARL AU",
            "capital_social": -1000,
            "siege_social": "12 rue des Fleurs, Casablanca",
        },
    )
    assert reponse.status_code == 422


def test_evaluer_dossier_forme_juridique_hors_perimetre() -> None:
    """Une forme juridique non couverte (SA) doit être signalée comme non conforme."""
    client = _nouveau_client()
    dossier = _creer_dossier(
        client,
        forme_juridique="SA",
        capital_social=300000,
        siege_social="Zone industrielle, Tanger",
    )
    client.patch(
        f"/dossiers/{dossier['id']}",
        json={
            "statuts_fournis": True,
            "certificat_negatif_fourni": True,
            "certificat_negatif_date_delivrance": "2026-07-15",
            "attestation_blocage_bancaire_fournie": True,
            "taxe_professionnelle_declaree": True,
        },
    )

    reponse = client.post(f"/dossiers/{dossier['id']}/evaluer")
    assert reponse.status_code == 201
    data = reponse.json()
    assert data["statut_global"] == "non_conforme"
    assert any(a["regle_id"] == "ID-000" for a in data["anomalies"])


def test_evaluer_dossier_inexistant_retourne_404() -> None:
    """Évaluer un dossier inexistant (ou appartenant à un autre) retourne 404."""
    client = _nouveau_client()
    reponse = client.post("/dossiers/00000000-0000-0000-0000-000000000000/evaluer")
    assert reponse.status_code == 404


def test_historique_evaluations_conserve_les_evaluations_precedentes() -> None:
    """Chaque évaluation est conservée, pas écrasée par la suivante (CONCEPTION_V2.md §9.4)."""
    client = _nouveau_client()
    dossier = _creer_dossier(client)

    client.post(f"/dossiers/{dossier['id']}/evaluer")
    client.post(f"/dossiers/{dossier['id']}/evaluer")

    reponse = client.get(f"/dossiers/{dossier['id']}/evaluations")
    assert reponse.status_code == 200
    assert len(reponse.json()) == 2


# """Test d'intégration du routeur /dossiers (cycle de vie persistant, CONCEPTION_V2.md §5)."""

# from collections.abc import Generator

# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy.pool import StaticPool

# from backend.core.database import get_db
# from backend.core.dependencies import UtilisateurConnecte, obtenir_utilisateur_connecte
# from backend.main import app
# from backend.models import Base


# def _nouveau_client() -> TestClient:
#     moteur = create_engine(
#         "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
#     )
#     Base.metadata.create_all(moteur)
#     fabrique_session = sessionmaker(bind=moteur)

#     def _remplacer_get_db() -> Generator[Session, None, None]:
#         session = fabrique_session()
#         try:
#             yield session
#         finally:
#             session.close()

#     app.dependency_overrides[get_db] = _remplacer_get_db
#     app.dependency_overrides[obtenir_utilisateur_connecte] = lambda: UtilisateurConnecte(
#         id="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee", email="test@example.com", role="entrepreneur"
#     )
#     return TestClient(app)


# def _creer_dossier(client: TestClient, **kwargs: object) -> dict:
#     payload = {
#         "nom_projet": "Mon projet",
#         "forme_juridique": "SARL AU",
#         "capital_social": 50000,
#         "siege_social": "12 rue des Fleurs, Casablanca",
#     }
#     payload.update(kwargs)
#     reponse = client.post("/dossiers", json=payload)
#     assert reponse.status_code == 201, reponse.text
#     return reponse.json()


# def test_evaluer_dossier_valide_retourne_conforme() -> None:
#     """Un dossier complet et cohérent doit être évalué comme conforme."""
#     client = _nouveau_client()
#     dossier = _creer_dossier(client)

#     client.patch(
#         f"/dossiers/{dossier['id']}",
#         json={
#             "statuts_fournis": True,
#             "certificat_negatif_fourni": True,
#             "certificat_negatif_date_delivrance": "2026-07-15",
#             "attestation_blocage_bancaire_fournie": False,
#             "taxe_professionnelle_declaree": True,
#             "affiliation_cnss_fournie": False,
#         },
#     )
#     client.post(
#         f"/dossiers/{dossier['id']}/identites",
#         json={
#             "nom": "Alaoui",
#             "prenom": "Yasmine",
#             "numero_cin": "BE123456",
#             "date_naissance": "1990-05-14",
#         },
#     )

#     reponse = client.post(f"/dossiers/{dossier['id']}/evaluer")
#     assert reponse.status_code == 201
#     assert reponse.json()["statut_global"] == "conforme"


# def test_creer_dossier_capital_negatif_est_rejete_par_validation() -> None:
#     """Un capital social négatif ou nul doit être rejeté au niveau du schéma (422)."""
#     client = _nouveau_client()
#     reponse = client.post(
#         "/dossiers",
#         json={
#             "nom_projet": "Mon projet",
#             "forme_juridique": "SARL AU",
#             "capital_social": -1000,
#             "siege_social": "12 rue des Fleurs, Casablanca",
#         },
#     )
#     assert reponse.status_code == 422


# def test_evaluer_dossier_forme_juridique_hors_perimetre() -> None:
#     """Une forme juridique non couverte (SA) doit être signalée comme non conforme."""
#     client = _nouveau_client()
#     dossier = _creer_dossier(
#         client,
#         forme_juridique="SA",
#         capital_social=300000,
#         siege_social="Zone industrielle, Tanger",
#     )
#     client.patch(
#         f"/dossiers/{dossier['id']}",
#         json={
#             "statuts_fournis": True,
#             "certificat_negatif_fourni": True,
#             "certificat_negatif_date_delivrance": "2026-07-15",
#             "attestation_blocage_bancaire_fournie": True,
#             "taxe_professionnelle_declaree": True,
#         },
#     )

#     reponse = client.post(f"/dossiers/{dossier['id']}/evaluer")
#     assert reponse.status_code == 201
#     data = reponse.json()
#     assert data["statut_global"] == "non_conforme"
#     assert any(a["regle_id"] == "ID-000" for a in data["anomalies"])


# def test_evaluer_dossier_inexistant_retourne_404() -> None:
#     """Évaluer un dossier inexistant (ou appartenant à un autre) retourne 404."""
#     client = _nouveau_client()
#     reponse = client.post("/dossiers/00000000-0000-0000-0000-000000000000/evaluer")
#     assert reponse.status_code == 404


# def test_historique_evaluations_conserve_les_evaluations_precedentes() -> None:
#     """Chaque évaluation est conservée, pas écrasée par la suivante (CONCEPTION_V2.md §9.4)."""
#     client = _nouveau_client()
#     dossier = _creer_dossier(client)

#     client.post(f"/dossiers/{dossier['id']}/evaluer")
#     client.post(f"/dossiers/{dossier['id']}/evaluer")

#     reponse = client.get(f"/dossiers/{dossier['id']}/evaluations")
#     assert reponse.status_code == 200
#     assert len(reponse.json()) == 2
