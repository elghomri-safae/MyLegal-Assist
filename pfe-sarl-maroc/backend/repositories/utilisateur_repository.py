"""Repository d'accès aux données pour l'entité Utilisateur (SQLAlchemy)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.utilisateur import Utilisateur


class UtilisateurRepository:
    """Accès aux données des utilisateurs, isolé de la logique métier (auth_service)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def obtenir_par_email(self, email: str) -> Utilisateur | None:
        """Retourne l'utilisateur correspondant à l'email, ou None si absent."""
        return self._db.query(Utilisateur).filter(Utilisateur.email == email).one_or_none()

    def creer(self, nom: str, email: str, role: str, mot_de_passe_hash: str) -> Utilisateur:
        """Crée et persiste un nouvel utilisateur."""
        utilisateur = Utilisateur(
            nom=nom, email=email, role=role, mot_de_passe_hash=mot_de_passe_hash
        )
        self._db.add(utilisateur)
        self._db.commit()
        self._db.refresh(utilisateur)
        return utilisateur
