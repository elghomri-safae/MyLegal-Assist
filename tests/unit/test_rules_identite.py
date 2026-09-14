"""Tests unitaires des règles de la catégorie 'identite'."""

from backend.rules.identite import RULES
from backend.schemas.dossier import DossierInput, IdentitePersonneInput

_REGLES = {r.meta.id: r for r in RULES}


def _dossier(**overrides: object) -> DossierInput:
    base = {
        "forme_juridique": "SARL AU",
        "capital_social": 50000,
        "identites": [IdentitePersonneInput(nom="Test", prenom="Test", numero_cin="AA000000")],
    }
    base.update(overrides)
    return DossierInput.model_validate(base)


def test_id_000_forme_non_couverte() -> None:
    """Une forme juridique hors SARL/SARL AU doit déclencher ID-000."""
    dossier = _dossier(forme_juridique="SAS")
    assert _REGLES["ID-000"].est_declenchee(dossier) is True


def test_id_000_ne_se_declenche_pas_pour_sarl() -> None:
    """SARL et SARL AU ne doivent jamais déclencher ID-000."""
    assert _REGLES["ID-000"].est_declenchee(_dossier(forme_juridique="SARL")) is False
    assert _REGLES["ID-000"].est_declenchee(_dossier(forme_juridique="SARL AU")) is False


def test_id_002_sarl_au_avec_deux_associes() -> None:
    """Une SARL AU avec deux associés doit déclencher ID-002."""
    dossier = _dossier(
        forme_juridique="SARL AU",
        identites=[
            IdentitePersonneInput(nom="A", prenom="A", numero_cin="AA111111"),
            IdentitePersonneInput(nom="B", prenom="B", numero_cin="AA222222"),
        ],
    )
    assert _REGLES["ID-002"].est_declenchee(dossier) is True


def test_id_001_sarl_avec_un_associe_est_valide() -> None:
    """Une SARL avec un seul associé (dans [1,50]) ne doit pas déclencher ID-001."""
    dossier = _dossier(forme_juridique="SARL")
    assert _REGLES["ID-001"].est_declenchee(dossier) is False


def test_id_003_identite_sans_cin() -> None:
    """Une identité sans numéro de CIN doit déclencher ID-003."""
    dossier = _dossier(identites=[IdentitePersonneInput(nom="X", prenom="Y", numero_cin="")])
    assert _REGLES["ID-003"].est_declenchee(dossier) is True
