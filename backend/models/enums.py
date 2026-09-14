


"""Shared enumerations used across ORM models.

Ces enumerations formalisent les vocabulaires fermes issus de la conception
UML (docs/UML.md, Phase 1) : roles applicatifs, statuts de dossier, gravite
des anomalies, etc.

MODIFICATION (positions métier MyLegal — référentiel documentaire) : ajout
de ``TypeJustificatifSiegeEnum`` et ``TypeApportEnum``, nécessaires pour
distinguer les cas 🟢 (client fournit) / 🟠 (MyLegal produit) sur le
justificatif de siège, et pour exclure les dossiers avec apport en nature
du traitement automatisé (hors périmètre v1).
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
    HORS_PERIMETRE_AUTOMATISE = "hors_perimetre_automatise"


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


class TypeJustificatifSiegeEnum(str, enum.Enum):
    """Type de justificatif de siège social (position MyLegal, référentiel
    documentaire §DOC-002).

    ``DOMICILIATION_MYLEGAL`` est le seul cas où le document est produit par
    MyLegal (🟠) plutôt que fourni par le client (🟢, les trois autres cas).
    """

    BAIL = "bail"
    DOMICILIATION_MYLEGAL = "domiciliation_myLegal"
    DOMICILIATION_TIERS = "domiciliation_tiers"
    PROPRIETE = "propriete"


class TypeApportEnum(str, enum.Enum):
    """Nature de l'apport au capital (position MyLegal : l'apport en nature
    est hors périmètre v1, exclu du traitement automatisé)."""

    NUMERAIRE = "numeraire"
    NATURE = "nature"

class TypePieceEnum(str, enum.Enum):
    """Types de pièces justificatives suivies pour un dossier (Problème 1)."""

    STATUTS = "statuts"
    CERTIFICAT_NEGATIF = "certificat_negatif"
    ATTESTATION_BLOCAGE_BANCAIRE = "attestation_blocage_bancaire"
    TAXE_PROFESSIONNELLE = "taxe_professionnelle"
    AFFILIATION_CNSS = "affiliation_cnss"
    JUSTIFICATIF_SIEGE = "justificatif_siege"
    PV_NOMINATION_GERANT = "pv_nomination_gerant"