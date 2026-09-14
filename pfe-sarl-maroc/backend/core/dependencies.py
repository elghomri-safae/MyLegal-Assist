"""Dépendances FastAPI d'authentification et de contrôle d'accès par rôle.

Implémentation d'authentification simplifiée (jeton JWT porteur), pas un
flux OAuth2 complet : ``OAuth2PasswordBearer`` n'est utilisé ici que pour
bénéficier du bouton « Authorize » de la documentation Swagger générée par
FastAPI ; le routeur ``/auth/connexion`` accepte un corps JSON classique,
pas un encodage de formulaire OAuth2 (voir DECISIONS.md, Phase 6).
"""

from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.core.security import decoder_jeton_acces

_schema_porteur_jeton = OAuth2PasswordBearer(tokenUrl="/auth/connexion")


@dataclass(frozen=True)
class UtilisateurConnecte:
    """Identité et rôle de l'utilisateur authentifié, extraits du jeton JWT."""

    id: str
    email: str
    role: str


def obtenir_utilisateur_connecte(
    jeton: str = Depends(_schema_porteur_jeton),
) -> UtilisateurConnecte:
    """Décode le jeton JWT porteur et retourne l'identité de l'utilisateur authentifié."""
    try:
        charge_utile = decoder_jeton_acces(jeton)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide ou expiré.",
        ) from exc

    return UtilisateurConnecte(
        id=charge_utile["sub"], email=charge_utile["email"], role=charge_utile["role"]
    )


def exiger_role(*roles_autorises: str):  # type: ignore[no-untyped-def]
    """Fabrique une dépendance FastAPI exigeant que l'utilisateur ait un des rôles fournis."""

    def dependance(
        utilisateur: UtilisateurConnecte = Depends(obtenir_utilisateur_connecte),
    ) -> UtilisateurConnecte:
        if utilisateur.role not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès réservé aux rôles : {', '.join(roles_autorises)}.",
            )
        return utilisateur

    return dependance
