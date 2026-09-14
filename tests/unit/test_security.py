"""Tests unitaires du hachage de mot de passe et des jetons JWT (backend/core/security.py)."""

import jwt
import pytest

from backend.core.security import (
    creer_jeton_acces,
    decoder_jeton_acces,
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)


def test_hacher_puis_verifier_mot_de_passe_correct() -> None:
    """Un mot de passe correct doit être validé contre son propre hash."""
    mot_de_passe_hash = hacher_mot_de_passe("SuperSecret123")

    assert verifier_mot_de_passe("SuperSecret123", mot_de_passe_hash) is True


def test_verifier_mot_de_passe_incorrect() -> None:
    """Un mot de passe incorrect ne doit jamais être validé."""
    mot_de_passe_hash = hacher_mot_de_passe("SuperSecret123")

    assert verifier_mot_de_passe("MauvaisMotDePasse", mot_de_passe_hash) is False


def test_deux_hachages_du_meme_mot_de_passe_sont_differents() -> None:
    """Le sel aléatoire doit produire des hachages différents pour un même mot de passe."""
    assert hacher_mot_de_passe("abc") != hacher_mot_de_passe("abc")


def test_verifier_mot_de_passe_avec_hash_malforme_retourne_faux() -> None:
    """Un hash malformé (sans séparateur) ne doit jamais lever d'exception."""
    assert verifier_mot_de_passe("abc", "hash-invalide-sans-separateur") is False


def test_creer_puis_decoder_jeton_acces() -> None:
    """Un jeton créé doit être décodable et restituer l'identité fournie."""
    jeton = creer_jeton_acces(utilisateur_id="123", email="a@b.com", role="entrepreneur")

    charge_utile = decoder_jeton_acces(jeton)

    assert charge_utile["sub"] == "123"
    assert charge_utile["email"] == "a@b.com"
    assert charge_utile["role"] == "entrepreneur"


def test_decoder_jeton_invalide_leve_erreur() -> None:
    """Un jeton syntaxiquement invalide doit lever une exception PyJWT."""
    with pytest.raises(jwt.PyJWTError):
        decoder_jeton_acces("jeton.invalide.xyz")
