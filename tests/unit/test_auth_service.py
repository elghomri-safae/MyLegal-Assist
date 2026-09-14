"""Tests unitaires du service d'authentification (backend/services/auth_service.py).

Portent en particulier sur la correction du canal auxiliaire temporel :
authentifier_utilisateur() doit exécuter la vérification PBKDF2 même quand
l'email n'existe pas, pour ne pas permettre l'énumération de comptes par
mesure du temps de réponse.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from backend.schemas.auth import UtilisateurConnexion
from backend.services.auth_service import IdentifiantsInvalidesError, authentifier_utilisateur


class _RepositoryFactice:
    """Repository factice : ne connaît aucun utilisateur."""

    def __init__(self, _db: object) -> None:
        pass

    def obtenir_par_email(self, _email: str) -> None:
        return None


def test_connexion_email_inexistant_execute_quand_meme_la_verification_pbkdf2() -> None:
    """Même sans utilisateur trouvé, verifier_mot_de_passe doit être appelée.

    C'est ce qui garantit un temps de réponse comparable à celui d'un email
    existant avec mauvais mot de passe, empêchant l'énumération d'emails.
    """
    with (
        patch("backend.services.auth_service.UtilisateurRepository", _RepositoryFactice),
        patch(
            "backend.services.auth_service.verifier_mot_de_passe", return_value=False
        ) as verification_mockee,
    ):
        with pytest.raises(IdentifiantsInvalidesError):
            authentifier_utilisateur(
                db=object(),  # type: ignore[arg-type]
                payload=UtilisateurConnexion(
                    email="inconnu@example.com", mot_de_passe="peu importe"
                ),
            )

    verification_mockee.assert_called_once()
    args, _ = verification_mockee.call_args
    assert args[0] == "peu importe"
    # Le hash comparé doit être le hash factice de référence, jamais None
    # ni une chaîne vide, pour que le coût PBKDF2 soit bien celui d'une
    # vérification réelle.
    assert args[1] is not None
    assert "$" in args[1]
