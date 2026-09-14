"""Extraction des documents bruts du corpus documentaire fermé (data/raw/).

Corpus fermé (Règle absolue n°1/n°2) : uniquement les 6 documents fournis
(S1 à S6, voir PROJECT.md et data/raw/README.md). Aucune source externe
n'est ajoutée par ce module.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

RACINE_CORPUS_PAR_DEFAUT = Path(__file__).resolve().parents[2] / "data" / "raw"


@dataclass(frozen=True)
class DocumentBrut:
    """Un document source du corpus, avec ses métadonnées documentaires."""

    titre: str
    niveau: int
    type_source: str
    nom_fichier: str


CATALOGUE_CORPUS: tuple[DocumentBrut, ...] = (
    DocumentBrut(
        titre="Loi n5-96 sur la SNC, SCS, SCA, SARL et societe en participation",
        niveau=1,
        type_source="texte_de_loi",
        nom_fichier="loi_5-96.txt",
    ),
    DocumentBrut(
        titre="Impot sur les societes (IS) - Direction Generale des Impots",
        niveau=2,
        type_source="source_officielle",
        nom_fichier="impot_sur_societes.txt",
    ),
    DocumentBrut(
        titre="Taxe sur la valeur ajoutee (TVA) - Direction Generale des Impots",
        niveau=2,
        type_source="source_officielle",
        nom_fichier="tva.txt",
    ),
    DocumentBrut(
        titre="OMPIC - Registre Central du Commerce - Creation et vie de l'entreprise",
        niveau=2,
        type_source="source_officielle",
        nom_fichier="ompic_etapes_creation.txt",
    ),
    DocumentBrut(
        titre="Dar Al Moukawil - Guide 1 - Demarches administratives de creation d'entreprise",
        niveau=2,
        type_source="source_officielle",
        nom_fichier="dar_al_moukawil_guide.txt",
    ),
    DocumentBrut(
        titre="Documentation pratique - Creation de SARL / SARL AU au Maroc",
        niveau=3,
        type_source="guide_pratique",
        nom_fichier="creation_sarl_maroc.txt",
    ),
)


def lire_document(document: DocumentBrut, racine: Path = RACINE_CORPUS_PAR_DEFAUT) -> str:
    """Lit le contenu texte brut d'un document du corpus depuis ``data/raw/``."""
    chemin = racine / document.nom_fichier
    return chemin.read_text(encoding="utf-8")


def extraire_corpus(
    racine: Path = RACINE_CORPUS_PAR_DEFAUT,
) -> list[tuple[DocumentBrut, str]]:
    """Extrait le texte brut de l'ensemble des documents du corpus fermé."""
    return [(document, lire_document(document, racine)) for document in CATALOGUE_CORPUS]
