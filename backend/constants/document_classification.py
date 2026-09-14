"""Classification centralisée des pièces du dossier (client vs cabinet).

Source de vérité unique consultée à la fois par le système expert
(backend/rules/*.py, pour la gravité des anomalies) et par le frontend
(frontend/pages/Evaluation_Dossier.py, pour les badges d'affichage) —
élimine le risque de désynchronisation entre les deux (cf. l'incident
CAP-002 rencontré en développement, où deux sources indépendantes du même
choix métier avaient divergé).

Exception assumée : le justificatif de siège social n'est PAS dans cette
table. Sa classification dépend d'un choix dynamique de l'utilisateur
(domiciliation_myLegal => cabinet, les 3 autres types => client), pas
d'une valeur fixe par type de pièce — logique dédiée conservée dans
Evaluation_Dossier.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Gravite = Literal["bloquante", "avertissement", "informative"]
Responsable = Literal["client", "cabinet"]

GRAVITE_PAR_DEFAUT: Gravite = "bloquante"
RESPONSABLE_PAR_DEFAUT: Responsable = "client"


@dataclass(frozen=True)
class ClassificationPiece:
    """Classification d'une pièce : gravité en cas d'absence, responsable, libellé."""

    gravite: Gravite
    responsable: Responsable
    label: str


CLASSIFICATION_PIECES: dict[str, ClassificationPiece] = {
    "statuts": ClassificationPiece(
        gravite="bloquante", responsable="client", label="Statuts de la société"
    ),
    "attestation_blocage_bancaire": ClassificationPiece(
        gravite="bloquante", responsable="client", label="Attestation de blocage bancaire"
    ),
    "cin": ClassificationPiece(
        gravite="bloquante", responsable="client", label="Pièce d'identité de chaque associé"
    ),
    "certificat_negatif": ClassificationPiece(
        gravite="informative", responsable="cabinet", label="Certificat négatif"
    ),
    "taxe_professionnelle": ClassificationPiece(
        gravite="informative", responsable="cabinet", label="Déclaration à la taxe professionnelle"
    ),
    "affiliation_cnss": ClassificationPiece(
        gravite="informative", responsable="cabinet", label="Affiliation CNSS"
    ),
    "pv_nomination_gerant": ClassificationPiece(
        gravite="informative", responsable="cabinet", label="PV de nomination du gérant"
    ),
}


def get_gravite(type_piece: str) -> Gravite:
    """Gravité d'une pièce ; 'bloquante' par défaut si non répertoriée
    (prudence : mieux vaut bloquer à tort une pièce inconnue que laisser
    passer un dossier incomplet sans avertissement)."""
    classification = CLASSIFICATION_PIECES.get(type_piece)
    return classification.gravite if classification else GRAVITE_PAR_DEFAUT


def get_responsable(type_piece: str) -> Responsable:
    """Responsable d'une pièce ; 'client' par défaut si non répertoriée
    (prudence : ne jamais supposer à tort qu'une pièce inconnue est prise
    en charge par MyLegal)."""
    classification = CLASSIFICATION_PIECES.get(type_piece)
    return classification.responsable if classification else RESPONSABLE_PAR_DEFAUT


def get_label(type_piece: str) -> str:
    """Libellé d'affichage d'une pièce ; le type_piece brut par défaut."""
    classification = CLASSIFICATION_PIECES.get(type_piece)
    return classification.label if classification else type_piece


