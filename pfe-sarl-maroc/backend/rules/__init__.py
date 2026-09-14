"""Package du système expert anti-rejet — voir backend/RULES.md pour le catalogue complet."""

from backend.rules.capital import RULES as CAPITAL_RULES
from backend.rules.cnss import RULES as CNSS_RULES
from backend.rules.documents import RULES as DOCUMENTS_RULES
from backend.rules.fiscalite import RULES as FISCALITE_RULES
from backend.rules.identite import RULES as IDENTITE_RULES

ALL_RULES = [
    *IDENTITE_RULES,
    *DOCUMENTS_RULES,
    *CAPITAL_RULES,
    *FISCALITE_RULES,
    *CNSS_RULES,
]

__all__ = ["ALL_RULES"]
