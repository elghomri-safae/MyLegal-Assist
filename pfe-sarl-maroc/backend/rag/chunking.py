"""Découpage des documents nettoyés en chunks indexables.

Utilise ``langchain_text_splitters`` (dépendance du package ``langchain``
imposé par le cahier des charges) plutôt qu'une implémentation maison, pour
un découpage récursif respectant les frontières naturelles du texte
(paragraphes, phrases) avant de forcer une coupe caractère par caractère.
"""

from __future__ import annotations

from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.rag.cleaning import DocumentNettoye

TAILLE_CHUNK_CARACTERES = 800
CHEVAUCHEMENT_CARACTERES = 120


@dataclass(frozen=True)
class ChunkDocument:
    """Un fragment de texte indexable, avec les métadonnées de sa source."""

    document_titre: str
    niveau: int
    type_source: str
    position: int
    texte: str


def _construire_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=TAILLE_CHUNK_CARACTERES,
        chunk_overlap=CHEVAUCHEMENT_CARACTERES,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def decouper_document(document: DocumentNettoye) -> list[ChunkDocument]:
    """Découpe un document nettoyé en chunks avec chevauchement."""
    splitter = _construire_splitter()
    fragments = splitter.split_text(document.texte)
    return [
        ChunkDocument(
            document_titre=document.titre,
            niveau=document.niveau,
            type_source=document.type_source,
            position=position,
            texte=fragment,
        )
        for position, fragment in enumerate(fragments)
    ]


def decouper_corpus(documents: list[DocumentNettoye]) -> list[ChunkDocument]:
    """Découpe l'ensemble des documents nettoyés du corpus."""
    chunks: list[ChunkDocument] = []
    for document in documents:
        chunks.extend(decouper_document(document))
    return chunks
