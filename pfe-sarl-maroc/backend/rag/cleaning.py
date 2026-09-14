"""Nettoyage du texte brut extrait (uniformisation des espaces, sauts de ligne)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from backend.rag.extraction import DocumentBrut

_ESPACES_MULTIPLES = re.compile(r"[ \t]+")
_LIGNES_VIDES_MULTIPLES = re.compile(r"\n{3,}")


@dataclass(frozen=True)
class DocumentNettoye:
    """Un document du corpus après nettoyage textuel, prêt pour le découpage."""

    titre: str
    niveau: int
    type_source: str
    texte: str


def nettoyer_texte(texte_brut: str) -> str:
    """Uniformise les espaces et supprime les sauts de ligne excessifs."""
    texte = texte_brut.replace("\r\n", "\n").replace("\r", "\n")
    texte = _ESPACES_MULTIPLES.sub(" ", texte)
    texte = _LIGNES_VIDES_MULTIPLES.sub("\n\n", texte)
    return texte.strip()


def nettoyer_document(document: DocumentBrut, texte_brut: str) -> DocumentNettoye:
    """Applique le nettoyage à un document et conserve ses métadonnées."""
    return DocumentNettoye(
        titre=document.titre,
        niveau=document.niveau,
        type_source=document.type_source,
        texte=nettoyer_texte(texte_brut),
    )


def nettoyer_corpus(documents_bruts: list[tuple[DocumentBrut, str]]) -> list[DocumentNettoye]:
    """Nettoie l'ensemble des documents extraits du corpus."""
    return [nettoyer_document(document, texte) for document, texte in documents_bruts]
