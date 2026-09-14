"""Tests unitaires des règles des catégories 'fiscalite' et 'cnss'."""

from backend.rules.cnss import RULES as CNSS_RULES
from backend.rules.fiscalite import RULES as FISCALITE_RULES
from backend.schemas.dossier import DossierInput

_FISC = {r.meta.id: r for r in FISCALITE_RULES}
_CNSS = {r.meta.id: r for r in CNSS_RULES}


def _dossier(**overrides: object) -> DossierInput:
    base = {
        "forme_juridique": "SARL",
        "capital_social": 50000,
        "taxe_professionnelle_declaree": True,
        "emploie_salaries": False,
        "affiliation_cnss_fournie": False,
    }
    base.update(overrides)
    return DossierInput.model_validate(base)


def test_fisc_001_taxe_professionnelle_non_declaree() -> None:
    """L'absence de déclaration de taxe professionnelle doit déclencher FISC-001."""
    dossier = _dossier(taxe_professionnelle_declaree=False)
    assert _FISC["FISC-001"].est_declenchee(dossier) is True


def test_fisc_002_est_toujours_declenchee_a_titre_informatif() -> None:
    """FISC-002 est un rappel systématique, quelle que soit la complétude du dossier."""
    dossier = _dossier()
    assert _FISC["FISC-002"].est_declenchee(dossier) is True
    assert _FISC["FISC-002"].meta.gravite == "informative"


def test_cnss_001_salaries_sans_affiliation() -> None:
    """Des salariés employés sans affiliation CNSS doivent déclencher CNSS-001."""
    dossier = _dossier(emploie_salaries=True, affiliation_cnss_fournie=False)
    assert _CNSS["CNSS-001"].est_declenchee(dossier) is True
    assert _CNSS["CNSS-001"].meta.gravite == "avertissement"


def test_cnss_001_sans_salaries_ne_se_declenche_pas() -> None:
    """Sans salarié déclaré, CNSS-001 ne doit pas se déclencher."""
    dossier = _dossier(emploie_salaries=False)
    assert _CNSS["CNSS-001"].est_declenchee(dossier) is False
