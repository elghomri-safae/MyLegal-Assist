"""Tests d'intégration du système expert anti-rejet sur des dossiers synthétiques.

Couvre les cas exigés par le cahier des charges : valide, incomplet,
incohérent, certificat négatif absent, siège social manquant, mauvaise
forme juridique, plus un cas isolant la règle de blocage du capital.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.schemas.dossier import DossierInput
from backend.services.expert_service import evaluer_dossier

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "data" / "synthetic"

CAS_ATTENDUS: dict[str, dict[str, object]] = {
    "dossier_valide.json": {
        "statut_global": "conforme",
        "regles_bloquantes_attendues": set(),
    },
    "dossier_incomplet.json": {
        "statut_global": "non_conforme",
        "regles_bloquantes_attendues": {
            "ID-001",
            "ID-003",
            "DOC-001",
            "DOC-002",
            "DOC-003",
            "FISC-001",
        },
    },
    "dossier_incoherent.json": {
        "statut_global": "non_conforme",
        "regles_bloquantes_attendues": {"ID-002"},
    },
    "dossier_certificat_negatif_absent.json": {
        "statut_global": "non_conforme",
        "regles_bloquantes_attendues": {"DOC-001"},
    },
    "dossier_siege_social_manquant.json": {
        "statut_global": "non_conforme",
        "regles_bloquantes_attendues": {"DOC-002"},
    },
    "dossier_mauvaise_forme_juridique.json": {
        "statut_global": "non_conforme",
        "regles_bloquantes_attendues": {"ID-000"},
    },
    "dossier_capital_sans_blocage.json": {
        "statut_global": "non_conforme",
        "regles_bloquantes_attendues": {"CAP-001"},
    },
}


@pytest.mark.parametrize("nom_fichier", sorted(CAS_ATTENDUS))
def test_evaluation_dossier_synthetique(nom_fichier: str) -> None:
    """Chaque dossier synthétique doit produire le verdict et les règles attendus."""
    data = json.loads((FIXTURES_DIR / nom_fichier).read_text(encoding="utf-8"))
    dossier = DossierInput.model_validate(data)

    verdict = evaluer_dossier(dossier)

    attendu = CAS_ATTENDUS[nom_fichier]
    assert verdict.statut_global.value == attendu["statut_global"], nom_fichier

    regles_bloquantes_obtenues = {
        anomalie.regle_id for anomalie in verdict.anomalies if anomalie.gravite == "bloquante"
    }
    assert regles_bloquantes_obtenues == attendu["regles_bloquantes_attendues"], nom_fichier


def test_dossier_valide_contient_neanmoins_un_rappel_informatif() -> None:
    """FISC-002 (informative) est toujours présente mais ne degrade jamais le statut."""
    data = json.loads((FIXTURES_DIR / "dossier_valide.json").read_text(encoding="utf-8"))
    dossier = DossierInput.model_validate(data)

    verdict = evaluer_dossier(dossier)

    assert verdict.statut_global.value == "conforme"
    assert any(a.regle_id == "FISC-002" for a in verdict.anomalies)
