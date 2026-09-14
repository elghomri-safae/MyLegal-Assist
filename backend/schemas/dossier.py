"""Schémas Pydantic représentant un dossier de création soumis à évaluation.

MODIFICATION (cohérence MCD/code) : type_apport est retiré de Dossier — le
choix métier de nature de l'apport est désormais porté exclusivement par
chaque IdentitePersonne (type_apport_personnel), cohérent avec CAP-002 qui
ne lit plus que cette source. Un dossier est "hors périmètre" dès qu'un
seul associé déclare un apport en nature, sans qu'aucun choix global ne
soit nécessaire au niveau du dossier lui-même.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class IdentitePersonneInput(BaseModel):
    nom: str = ""
    prenom: str = ""
    numero_cin: str = ""
    date_naissance: date | None = None
    type_apport_personnel: str | None = None
    montant_apport: float | None = None


class IdentitePersonneUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    numero_cin: str | None = None
    date_naissance: date | None = None
    type_apport_personnel: str | None = None
    montant_apport: float | None = None


class IdentitePersonneRead(BaseModel):
    id: str
    nom: str | None
    prenom: str | None
    numero_cin: str | None
    date_naissance: date | None
    type_apport_personnel: str | None
    montant_apport: float | None


class PieceJustificativeInput(BaseModel):
    type_piece: str
    fournie: bool = False


class DossierInput(BaseModel):
    """Données d'un dossier de création soumises au système expert anti-rejet."""

    forme_juridique: str
    capital_social: float = Field(gt=0)
    siege_social: str = ""

    statuts_fournis: bool = False
    attestation_blocage_bancaire_fournie: bool = False

    emploie_salaries: bool = False

    type_justificatif_siege: str = ""
    gerant_designe_dans_statuts: bool = False

    identites: list[IdentitePersonneInput] = Field(default_factory=list)
    pieces: list[PieceJustificativeInput] = Field(default_factory=list)


class DossierCreate(BaseModel):
    nom_projet: str = Field(min_length=1)
    forme_juridique: str = Field(min_length=1)
    capital_social: float = Field(gt=0)
    siege_social: str = ""


class DossierUpdate(BaseModel):
    """Mise à jour progressive d'un dossier existant. Tous les champs optionnels."""

    nom_projet: str | None = Field(default=None, min_length=1)
    forme_juridique: str | None = Field(default=None, min_length=1)
    capital_social: float | None = Field(default=None, gt=0)
    siege_social: str | None = None
    statuts_fournis: bool | None = None
    attestation_blocage_bancaire_fournie: bool | None = None
    emploie_salaries: bool | None = None
    type_justificatif_siege: str | None = None
    gerant_designe_dans_statuts: bool | None = None


class DossierRead(BaseModel):
    id: str
    nom_projet: str
    forme_juridique: str
    capital_social: float
    siege_social: str
    statuts_fournis: bool
    attestation_blocage_bancaire_fournie: bool
    emploie_salaries: bool
    type_justificatif_siege: str
    gerant_designe_dans_statuts: bool
    statut: str
    date_creation: datetime

    progression_pct: int
    nb_erreurs_bloquantes: int
    nb_avertissements: int
    pret_pour_depot: bool
    date_derniere_evaluation: datetime | None

    identites: list[IdentitePersonneRead] = Field(default_factory=list)



class ClassificationPieceRead(BaseModel):
    type_piece: str
    responsable: str
    label: str