
"""Schémas Pydantic du module authentification (Phase 6).

MODIFICATION (Phase 1 — comptes créés par MyLegal) : ``UtilisateurInscription``
est retiré — il laissait n'importe quel appelant HTTP choisir librement son
propre ``role`` (y compris ``admin``), sans aucune restriction. Un compte
entrepreneur est désormais créé exclusivement par un administrateur
(``EntrepreneurCreation``, sans champ ``role`` : fixé côté serveur), et le
premier compte admin est créé hors-API par ``scripts/creer_admin.py``, jamais
via une route HTTP.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr

from backend.models.enums import RoleEnum


class EntrepreneurCreation(BaseModel):
    """Données fournies par un administrateur pour créer un compte entrepreneur.

    Pas de champ ``mot_de_passe`` ni ``role`` : le mot de passe temporaire
    est généré côté serveur (transmis une seule fois dans la réponse, à
    communiquer au client hors-bande par MyLegal), et le rôle est
    systématiquement ``entrepreneur``.
    """

    nom: str
    email: EmailStr


class EntrepreneurCree(BaseModel):
    """Réponse à la création d'un compte entrepreneur par un administrateur.

    ``mot_de_passe_temporaire`` n'apparaît QUE dans cette réponse, au moment
    de la création — jamais renvoyé ni stocké en clair ensuite (seul son
    hash l'est, comme pour tout mot de passe).
    """

    id: str
    nom: str
    email: EmailStr
    role: RoleEnum
    mot_de_passe_temporaire: str


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
