"""Tests unitaires des règles de la catégorie 'documents'."""

from datetime import date, timedelta

from backend.rules.documents import RULES
from backend.schemas.dossier import DossierInput

_REGLES = {r.meta.id: r for r in RULES}


def _dossier(**overrides: object) -> DossierInput:
    base = {
        "forme_juridique": "SARL AU",
        "capital_social": 50000,
        "siege_social": "Adresse test",
        "statuts_fournis": True,
        "certificat_negatif_fourni": True,
        "certificat_negatif_date_delivrance": date.today(),
    }
    base.update(overrides)
    return DossierInput.model_validate(base)


def test_doc_001_certificat_non_declare() -> None:
    """La case non cochée doit déclencher DOC-001, quelle que soit la date."""
    dossier = _dossier(certificat_negatif_fourni=False, certificat_negatif_date_delivrance=None)
    assert _REGLES["DOC-001"].est_declenchee(dossier) is True
    assert _REGLES["DOC-001B"].est_declenchee(dossier) is False


def test_doc_001_certificat_coche_sans_date_nest_pas_une_anomalie() -> None:
    """Régression : la case cochée sans date renseignée ne doit JAMAIS être
    traitée comme une expiration. Si l'utilisateur confirme disposer du
    certificat, le document est considéré comme disponible tant qu'aucune
    date n'a été demandée — ni DOC-001 ni DOC-001B ne doivent se déclencher.
    """
    dossier = _dossier(certificat_negatif_fourni=True, certificat_negatif_date_delivrance=None)
    assert _REGLES["DOC-001"].est_declenchee(dossier) is False
    assert _REGLES["DOC-001B"].est_declenchee(dossier) is False


def test_doc_001b_certificat_date_depassee() -> None:
    """Un certificat négatif délivré il y a plus de 90 jours doit déclencher
    DOC-001B, uniquement si une date a été explicitement renseignée."""
    dossier = _dossier(certificat_negatif_date_delivrance=date.today() - timedelta(days=200))
    assert _REGLES["DOC-001"].est_declenchee(dossier) is False
    assert _REGLES["DOC-001B"].est_declenchee(dossier) is True


def test_doc_001b_certificat_date_recente() -> None:
    """Un certificat négatif récent ne doit déclencher ni DOC-001 ni DOC-001B."""
    dossier = _dossier(certificat_negatif_date_delivrance=date.today() - timedelta(days=5))
    assert _REGLES["DOC-001"].est_declenchee(dossier) is False
    assert _REGLES["DOC-001B"].est_declenchee(dossier) is False


def test_doc_002_siege_social_manquant() -> None:
    """Un siège social vide doit déclencher DOC-002."""
    dossier = _dossier(siege_social="   ")
    assert _REGLES["DOC-002"].est_declenchee(dossier) is True


def test_doc_003_statuts_absents() -> None:
    """Des statuts non fournis doivent déclencher DOC-003."""
    dossier = _dossier(statuts_fournis=False)
    assert _REGLES["DOC-003"].est_declenchee(dossier) is True

# """Tests unitaires des règles de la catégorie 'documents'."""

# from datetime import date, timedelta

# from backend.rules.documents import RULES
# from backend.schemas.dossier import DossierInput

# _REGLES = {r.meta.id: r for r in RULES}


# def _dossier(**overrides: object) -> DossierInput:
#     base = {
#         "forme_juridique": "SARL AU",
#         "capital_social": 50000,
#         "siege_social": "Adresse test",
#         "statuts_fournis": True,
#         "certificat_negatif_fourni": True,
#         "certificat_negatif_date_delivrance": date.today(),
#     }
#     base.update(overrides)
#     return DossierInput.model_validate(base)


# def test_doc_001_certificat_absent() -> None:
#     """L'absence de certificat négatif doit déclencher DOC-001."""
#     dossier = _dossier(certificat_negatif_fourni=False, certificat_negatif_date_delivrance=None)
#     assert _REGLES["DOC-001"].est_declenchee(dossier) is True


# def test_doc_001_certificat_expire() -> None:
#     """Un certificat négatif délivré il y a plus de 90 jours doit déclencher DOC-001."""
#     dossier = _dossier(certificat_negatif_date_delivrance=date.today() - timedelta(days=200))
#     assert _REGLES["DOC-001"].est_declenchee(dossier) is True


# def test_doc_001_certificat_valide() -> None:
#     """Un certificat négatif récent ne doit pas déclencher DOC-001."""
#     dossier = _dossier(certificat_negatif_date_delivrance=date.today() - timedelta(days=5))
#     assert _REGLES["DOC-001"].est_declenchee(dossier) is False


# def test_doc_002_siege_social_manquant() -> None:
#     """Un siège social vide doit déclencher DOC-002."""
#     dossier = _dossier(siege_social="   ")
#     assert _REGLES["DOC-002"].est_declenchee(dossier) is True


# def test_doc_003_statuts_absents() -> None:
#     """Des statuts non fournis doivent déclencher DOC-003."""
#     dossier = _dossier(statuts_fournis=False)
#     assert _REGLES["DOC-003"].est_declenchee(dossier) is True
