# """Centralized application settings loaded from environment variables.

# Conformement a l'exigence de reproductibilite du cahier des charges, aucune
# valeur secrete (cle API, mot de passe) n'est codee en dur : tout provient de
# variables d'environnement, elles-memes chargees depuis un fichier ``.env``
# non versionne (voir ``.env.example``).
# """

# from functools import lru_cache

# from pydantic import Field, model_validator
# from pydantic_settings import BaseSettings, SettingsConfigDict

# _CLE_JWT_PAR_DEFAUT = "dev-secret-key-a-changer-en-production"


# class Settings(BaseSettings):
#     """Application-wide configuration values."""

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )

#     app_name: str = Field(default="PFE SARL Maroc")
#     app_env: str = Field(default="development")
#     debug: bool = Field(default=False)

#     database_url: str = Field(
#         default="postgresql+psycopg://postgres:postgres@localhost:5432/pfe_sarl_maroc"
#     )

#     chroma_persist_directory: str = Field(default="./data/embeddings")
#     groq_api_key: str = Field(default="")

#     # Cle de signature des jetons JWT (Phase 6). La valeur par defaut ne doit
#     # jamais etre utilisee en production : elle est ecrasee par la variable
#     # d'environnement SECRET_KEY (.env), jamais codee en dur pour un usage reel.
#     secret_key: str = Field(default=_CLE_JWT_PAR_DEFAUT)

#     log_level: str = Field(default="INFO")

#     @model_validator(mode="after")
#     def _interdire_cle_par_defaut_en_production(self) -> "Settings":
#         """Empeche un demarrage en production avec la cle de signature JWT par defaut.

#         Un jeton signe avec cette valeur codee en dur serait forgeable par
#         quiconque lit le code source (ce fichier est public) : accepter ce
#         risque silencieusement en production serait une faille de securite,
#         pas une simple negligence de configuration.
#         """
#         if self.app_env == "production" and self.secret_key == _CLE_JWT_PAR_DEFAUT:
#             raise ValueError(
#                 "SECRET_KEY doit etre definie explicitement (variable d'environnement) "
#                 "lorsque APP_ENV=production : la valeur par defaut est publique et "
#                 "rendrait les jetons JWT forgeables."
#             )
#         return self


# @lru_cache
# def get_settings() -> Settings:
#     """Return a cached ``Settings`` instance shared across the application."""
#     return Settings()

"""Centralized application settings loaded from environment variables.

Conformement a l'exigence de reproductibilite du cahier des charges, aucune
valeur secrete (cle API, mot de passe) n'est codee en dur : tout provient de
variables d'environnement, elles-memes chargees depuis un fichier ``.env``
non versionne (voir ``.env.example``).

MODIFICATION (intégration corpus juridique) : ajout de
``corpus_structurel_path``, le chemin vers le JSON brut produit par le
chunking structurel externe (``output6_structural/corpus_chunks.json``).
Utilisé uniquement par le script d'import ponctuel
(``scripts/importer_corpus_structurel.py``), qui le convertit vers le
format ``ChunkDocument`` et le sauvegarde à l'emplacement déjà utilisé par
``chunk_store.py`` (``CHEMIN_CHUNKS_PAR_DEFAUT``) — aucun autre changement
de convention.

CORRECTIF (diagnostic 401 Groq "Invalid API Key") : ``groq_api_key`` est
maintenant nettoyée (espaces/retours à la ligne en début/fin retirés) après
chargement. Un ``.env`` édité sous Windows peut introduire un ``\\r`` ou un
espace de fin de ligne invisible : la clé a alors la bonne longueur et le
bon préfixe en apparence, mais diffère caractère pour caractère de la vraie
clé, d'où un 401 côté serveur malgré une clé "correcte" à l'œil. Ce
nettoyage est sans effet si la clé était déjà propre.
"""

from functools import lru_cache

from pydantic import Field, field_validator, model_validator
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

    # Chemin du corpus juridique structurel brut (chunking article-first
    # externe, cf. corpus_loader.py). Utilisé une seule fois par le script
    # d'import pour peupler data/chunks/corpus_chunks.json (convention déjà
    # utilisée par chunk_store.py) ; pas lu directement par le pipeline RAG.
    corpus_structurel_path: str = Field(
        default="./data/corpus/output6_structural/corpus_chunks.json"
    )

    # Cle de signature des jetons JWT (Phase 6). La valeur par defaut ne doit
    # jamais etre utilisee en production : elle est ecrasee par la variable
    # d'environnement SECRET_KEY (.env), jamais codee en dur pour un usage reel.
    secret_key: str = Field(default=_CLE_JWT_PAR_DEFAUT)

    log_level: str = Field(default="INFO")

    @field_validator("groq_api_key", mode="after")
    @classmethod
    def _nettoyer_cle_groq(cls, valeur: str) -> str:
        """Retire les espaces/retours à la ligne parasites (``.env`` édité
        sous Windows, copier-coller) qui rendraient la clé invalide malgré
        une apparence correcte (même préfixe, même longueur affichée)."""
        return valeur.strip()

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
