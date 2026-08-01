"""Schémas Pydantic du module authentification (Phase 6)."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr

from backend.models.enums import RoleEnum


class UtilisateurInscription(BaseModel):
    """Données fournies pour créer un compte utilisateur."""

    nom: str
    email: EmailStr
    mot_de_passe: str
    role: RoleEnum


class UtilisateurConnexion(BaseModel):
    """Identifiants fournis pour se connecter."""

    email: EmailStr
    mot_de_passe: str


class UtilisateurPublic(BaseModel):
    """Représentation publique d'un utilisateur (sans le mot de passe)."""

    id: str
    nom: str
    email: EmailStr
    role: RoleEnum


class Token(BaseModel):
    """Jeton d'accès JWT retourné après une connexion réussie."""

    access_token: str
    token_type: str = "bearer"
