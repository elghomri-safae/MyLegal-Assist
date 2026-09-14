"""Tests unitaires des règles de la catégorie 'capital'."""

from backend.rules.capital import RULES
from backend.schemas.dossier import DossierInput

_REGLES = {r.meta.id: r for r in RULES}


def _dossier(**overrides: object) -> DossierInput:
    base = {
        "forme_juridique": "SARL",
        "capital_social": 50000,
        "attestation_blocage_bancaire_fournie": False,
    }
    base.update(overrides)
    return DossierInput.model_validate(base)


def test_cap_001_capital_superieur_au_seuil_sans_attestation() -> None:
    """Un capital > 100 000 DH sans attestation de blocage doit déclencher CAP-001."""
    dossier = _dossier(capital_social=250000, attestation_blocage_bancaire_fournie=False)
    assert _REGLES["CAP-001"].est_declenchee(dossier) is True


def test_cap_001_capital_superieur_au_seuil_avec_attestation() -> None:
    """Un capital > 100 000 DH avec attestation ne doit pas déclencher CAP-001."""
    dossier = _dossier(capital_social=250000, attestation_blocage_bancaire_fournie=True)
    assert _REGLES["CAP-001"].est_declenchee(dossier) is False


def test_cap_001_capital_sous_le_seuil_ne_declenche_jamais() -> None:
    """Un capital <= 100 000 DH ne doit jamais déclencher CAP-001, meme sans attestation."""
    dossier = _dossier(capital_social=100000, attestation_blocage_bancaire_fournie=False)
    assert _REGLES["CAP-001"].est_declenchee(dossier) is False
