"""Tests unitaires pour le chargement des parametres applicatifs."""

import pytest

from backend.config.settings import Settings


def test_settings_refuse_la_cle_par_defaut_en_production() -> None:
    """En production, demarrer avec la cle JWT par defaut doit etre bloque."""
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(app_env="production", secret_key="dev-secret-key-a-changer-en-production")


def test_settings_accepte_une_cle_explicite_en_production() -> None:
    """En production, une cle explicite (differente du defaut) doit etre acceptee."""
    settings = Settings(app_env="production", secret_key="une-cle-vraiment-secrete")

    assert settings.secret_key == "une-cle-vraiment-secrete"


def test_settings_default_values() -> None:
    """Les parametres doivent exposer des valeurs par defaut sensees."""
    settings = Settings()

    assert settings.app_name == "PFE SARL Maroc"
    assert settings.log_level == "INFO"
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_settings_is_cached() -> None:
    """get_settings() doit retourner la meme instance a chaque appel (lru_cache)."""
    from backend.config.settings import get_settings

    first = get_settings()
    second = get_settings()

    assert first is second
