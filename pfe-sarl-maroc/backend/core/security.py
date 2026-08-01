"""Hachage de mots de passe et gestion des jetons JWT (authentification, Phase 6).

Le hachage utilise PBKDF2-HMAC-SHA256 (bibliothèque standard ``hashlib``,
aucune dépendance supplémentaire) plutôt que bcrypt/argon2, afin de rester
dans l'esprit « dépendances minimales » déjà observé dans le projet (voir
DECISIONS.md, Phase 6). Les jetons JWT utilisent PyJWT (dépendance légère,
ajoutée pour cette phase).
"""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from backend.config.settings import get_settings

_ITERATIONS_PBKDF2 = 260_000
ALGORITHME_JWT = "HS256"
DUREE_VALIDITE_TOKEN_MINUTES = 60


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Hache un mot de passe avec PBKDF2-HMAC-SHA256 et un sel aléatoire."""
    sel = os.urandom(16)
    hash_binaire = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode("utf-8"), sel, _ITERATIONS_PBKDF2
    )
    return f"{sel.hex()}${hash_binaire.hex()}"


# Hash factice, de forme valide mais correspondant à un mot de passe
# aléatoire fixe qu'aucun utilisateur ne connaît. Sert uniquement à faire
# exécuter un calcul PBKDF2 complet (même coût en temps qu'une vérification
# réelle) quand l'email fourni à la connexion n'existe pas en base, afin
# qu'un attaquant ne puisse pas distinguer "email inexistant" de "email
# existant, mauvais mot de passe" par la seule mesure du temps de réponse
# (voir backend/services/auth_service.py, authentifier_utilisateur).
HASH_FACTICE_TEMPS_CONSTANT = hacher_mot_de_passe("hash-factice-non-attribuable-a-un-compte")


def verifier_mot_de_passe(mot_de_passe: str, mot_de_passe_hash: str) -> bool:
    """Vérifie un mot de passe contre son hash stocké (comparaison à temps constant)."""
    try:
        sel_hex, hash_hex = mot_de_passe_hash.split("$", 1)
    except ValueError:
        return False

    sel = bytes.fromhex(sel_hex)
    hash_attendu = bytes.fromhex(hash_hex)
    hash_calcule = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode("utf-8"), sel, _ITERATIONS_PBKDF2
    )
    return hmac.compare_digest(hash_calcule, hash_attendu)


def creer_jeton_acces(utilisateur_id: str, email: str, role: str) -> str:
    """Crée un jeton JWT signé contenant l'identité et le rôle de l'utilisateur."""
    parametres = get_settings()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=DUREE_VALIDITE_TOKEN_MINUTES)
    charge_utile = {"sub": utilisateur_id, "email": email, "role": role, "exp": expiration}
    return jwt.encode(charge_utile, parametres.secret_key, algorithm=ALGORITHME_JWT)


def decoder_jeton_acces(jeton: str) -> dict[str, Any]:
    """Décode et vérifie un jeton JWT ; lève ``jwt.PyJWTError`` si invalide ou expiré."""
    parametres = get_settings()
    return jwt.decode(jeton, parametres.secret_key, algorithms=[ALGORITHME_JWT])
