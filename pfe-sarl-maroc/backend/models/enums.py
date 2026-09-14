"""Shared enumerations used across ORM models.

Ces enumerations formalisent les vocabulaires fermes issus de la conception
UML (docs/UML.md, Phase 1) : roles applicatifs, statuts de dossier, gravite
des anomalies, etc.
"""

import enum


class RoleEnum(str, enum.Enum):
    """Roles applicatifs valides pour un utilisateur (CONCEPTION_V2.md §3)."""

    ENTREPRENEUR = "entrepreneur"
    ADMIN = "admin"


class StatutDossierEnum(str, enum.Enum):
    """Cycle de vie d'un dossier de creation (CONCEPTION_V2.md §5 : brouillon -> evalue)."""

    BROUILLON = "brouillon"
    EVALUE = "evalue"


class GraviteEnum(str, enum.Enum):
    """Niveau de gravite d'une anomalie detectee par le systeme expert."""

    BLOQUANTE = "bloquante"
    AVERTISSEMENT = "avertissement"
    INFORMATIVE = "informative"


class StatutGlobalEnum(str, enum.Enum):
    """Verdict global d'une evaluation de dossier."""

    CONFORME = "conforme"
    NON_CONFORME = "non_conforme"
    CONFORME_AVEC_RESERVES = "conforme_avec_reserves"
