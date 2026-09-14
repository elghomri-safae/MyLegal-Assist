
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ChunkDocument:

    document_titre: str
    type_source: str
    position: int
    texte: str
    niveau: int | None = None
    chunk_id: str | None = None
    article: str | None = None
    page: int | None = None
    section: str | None = None
    filename: str | None = None


# document_titre / filename ? Parce que ce sont deux usages différents : 
# filename sert à un audit technique exact (retrouver le fichier source précis), 
# document_titre sert à l'affichage humain 
# (l'utilisateur ne doit jamais voir "LOI-N°-5-96-Aout-2021.pdf" mais "Loi n° 5-96 relative à la SARL").