"""Centralized application settings loaded from environment variables.

Conformement a l'exigence de reproductibilite du cahier des charges, aucune
valeur secrete (cle API, mot de passe) n'est codee en dur : tout provient de
variables d'environnement, elles-memes chargees depuis un fichier ``.env``
non versionne (voir ``.env.example``).
"""

from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_CLE_JWT_PAR_DEFAUT = "dev-secret-key-a-changer-en-production"


class Settings(BaseSettings):
    """Application-wide configuration values."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="PFE SARL Maroc")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/pfe_sarl_maroc"
    )

    chroma_persist_directory: str = Field(default="./data/embeddings")
    groq_api_key: str = Field(default="")

    # Cle de signature des jetons JWT (Phase 6). La valeur par defaut ne doit
    # jamais etre utilisee en production : elle est ecrasee par la variable
    # d'environnement SECRET_KEY (.env), jamais codee en dur pour un usage reel.
    secret_key: str = Field(default=_CLE_JWT_PAR_DEFAUT)

    log_level: str = Field(default="INFO")

    @model_validator(mode="after")
    def _interdire_cle_par_defaut_en_production(self) -> "Settings":
        """Empeche un demarrage en production avec la cle de signature JWT par defaut.

        Un jeton signe avec cette valeur codee en dur serait forgeable par
        quiconque lit le code source (ce fichier est public) : accepter ce
        risque silencieusement en production serait une faille de securite,
        pas une simple negligence de configuration.
        """
        if self.app_env == "production" and self.secret_key == _CLE_JWT_PAR_DEFAUT:
            raise ValueError(
                "SECRET_KEY doit etre definie explicitement (variable d'environnement) "
                "lorsque APP_ENV=production : la valeur par defaut est publique et "
                "rendrait les jetons JWT forgeables."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance shared across the application."""
    return Settings()
