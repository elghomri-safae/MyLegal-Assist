"""Schémas Pydantic représentant un dossier de création soumis à évaluation.

Ces schémas forment la frontière (DTO) entre l'API/le service métier et les
modèles ORM (backend/models/dossier.py, identite_personne.py). Ils ne sont
volontairement pas identiques aux modèles ORM : ils exposent uniquement les
champs nécessaires à l'évaluation par le système expert.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class IdentitePersonneInput(BaseModel):
    """Identité d'un associé, telle que fournie manuellement."""

    nom: str = ""
    prenom: str = ""
    numero_cin: str = ""
    date_naissance: date | None = None


class PieceJustificativeInput(BaseModel):
    """Pièce justificative attachée au dossier."""

    type_piece: str
    fournie: bool = False


class DossierInput(BaseModel):
    """Données d'un dossier de création soumises au système expert anti-rejet."""

    forme_juridique: str
    # gt=0 : un capital social nul ou négatif n'a aucun sens juridique ou
    # comptable et ne doit jamais atteindre le système expert. Sans cette
    # contrainte, une valeur négative traversait la validation Pydantic sans
    # erreur et ne déclenchait aucune règle métier (CAP-001 ne teste que
    # "capital_social > 100000"), ce qui aurait produit un verdict "conforme"
    # pour un dossier manifestement invalide.
    capital_social: float = Field(gt=0)
    siege_social: str = ""

    statuts_fournis: bool = False

    certificat_negatif_fourni: bool = False
    certificat_negatif_date_delivrance: date | None = None

    attestation_blocage_bancaire_fournie: bool = False
    taxe_professionnelle_declaree: bool = False

    emploie_salaries: bool = False
    affiliation_cnss_fournie: bool = False

    identites: list[IdentitePersonneInput] = Field(default_factory=list)
    pieces: list[PieceJustificativeInput] = Field(default_factory=list)


def _valider_date_non_future(cls: type, valeur: date | None) -> date | None:  # noqa: ARG001
    """Validation structurelle de niveau 1 (CONCEPTION_V2.md §8) : une date de
    délivrance dans le futur n'a pas de sens, indépendamment de toute règle légale.

    Signature ``(cls, valeur)`` car ``field_validator`` transforme la
    fonction décorée en ``classmethod`` : ``cls`` est requis même s'il n'est
    pas utilisé ici.
    """
    if valeur is not None and valeur > date.today():
        raise ValueError("La date de délivrance du certificat négatif ne peut pas être future.")
    return valeur


class DossierCreate(BaseModel):
    """Données nécessaires à la création d'un dossier (CONCEPTION_V2.md §2, étape 3)."""

    nom_projet: str = Field(min_length=1)
    forme_juridique: str = Field(min_length=1)
    capital_social: float = Field(gt=0)
    siege_social: str = ""


class DossierUpdate(BaseModel):
    """Mise à jour progressive d'un dossier existant. Tous les champs optionnels :
    seuls ceux fournis sont modifiés (remplissage progressif, CONCEPTION_V2.md §2).
    """

    nom_projet: str | None = Field(default=None, min_length=1)
    forme_juridique: str | None = Field(default=None, min_length=1)
    capital_social: float | None = Field(default=None, gt=0)
    siege_social: str | None = None
    statuts_fournis: bool | None = None
    certificat_negatif_fourni: bool | None = None
    certificat_negatif_date_delivrance: date | None = None
    attestation_blocage_bancaire_fournie: bool | None = None
    taxe_professionnelle_declaree: bool | None = None
    emploie_salaries: bool | None = None
    affiliation_cnss_fournie: bool | None = None

    _valider_date = field_validator("certificat_negatif_date_delivrance")(_valider_date_non_future)


class DossierRead(BaseModel):
    """Représentation en lecture d'un dossier, incluant les indicateurs de
    tableau de bord (CONCEPTION_V2.md §9) : calculés à partir de la dernière
    évaluation et de l'état de saisie, jamais stockés tels quels.
    """

    id: str
    nom_projet: str
    forme_juridique: str
    capital_social: float
    siege_social: str
    statuts_fournis: bool
    certificat_negatif_fourni: bool
    certificat_negatif_date_delivrance: date | None
    attestation_blocage_bancaire_fournie: bool
    taxe_professionnelle_declaree: bool
    emploie_salaries: bool
    affiliation_cnss_fournie: bool
    statut: str
    date_creation: datetime

    # Indicateurs de tableau de bord (CONCEPTION_V2.md §9.1, §9.3) :
    # - progression_pct : proportion des champs structurants renseignés
    #   (nom_projet, forme_juridique, capital_social, siege_social, au moins
    #   une identité, date de délivrance du certificat négatif). Ne porte
    #   aucun jugement de conformité légale (§9.3) — les 5 indicateurs
    #   booléens "fourni"/"déclarée" ne sont volontairement pas comptés ici,
    #   car un booléen à False peut être une réponse réelle ("non, pas de
    #   salariés") aussi bien qu'une absence de saisie : les deux sont
    #   indiscernables avec le schéma actuel, donc exclus de la progression
    #   plutôt que comptés à tort comme "non complété".
    # - nb_erreurs_bloquantes / nb_avertissements (fusion avertissement +
    #   informative, §9.2) : portent sur la dernière évaluation uniquement.
    # - pret_pour_depot : vrai si le dernier verdict est conforme ou
    #   conforme_avec_reserves (§10.3 — proposition retenue).
    progression_pct: int
    nb_erreurs_bloquantes: int
    nb_avertissements: int
    pret_pour_depot: bool
    date_derniere_evaluation: datetime | None
