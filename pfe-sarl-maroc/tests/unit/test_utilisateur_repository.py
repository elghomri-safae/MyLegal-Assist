"""Test unitaire du repository Utilisateur, contre une base SQLite en mémoire réelle.

Contrairement aux autres tests du projet (qui substituent une session
factice), ce test exécute de vraies requêtes SQL via SQLAlchemy sur un
moteur SQLite en mémoire (bibliothèque standard, aucune dépendance
supplémentaire) : c'est un test d'intégration authentique du repository et
du modèle ORM, plus rigoureux qu'un simple test unitaire isolé.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.models import Base
from backend.repositories.utilisateur_repository import UtilisateurRepository


def _nouvelle_session_sqlite() -> Session:
    moteur = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(moteur)
    return sessionmaker(bind=moteur)()


def test_creer_puis_obtenir_par_email() -> None:
    """Un utilisateur créé doit être retrouvable par son email."""
    session = _nouvelle_session_sqlite()
    repository = UtilisateurRepository(session)

    repository.creer(
        nom="Alaoui",
        email="yasmine@example.com",
        role="entrepreneur",
        mot_de_passe_hash="sel$hash",
    )
    utilisateur = repository.obtenir_par_email("yasmine@example.com")

    assert utilisateur is not None
    assert utilisateur.nom == "Alaoui"
    assert utilisateur.role == "entrepreneur"


def test_obtenir_par_email_absent_retourne_none() -> None:
    """Un email inconnu doit retourner None, sans erreur."""
    session = _nouvelle_session_sqlite()
    repository = UtilisateurRepository(session)

    assert repository.obtenir_par_email("inconnu@example.com") is None
