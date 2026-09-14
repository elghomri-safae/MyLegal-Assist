"""Persistance simple des chunks du corpus (JSON).

Utilisée pour reconstruire l'index lexical BM25 au démarrage de l'API sans
avoir à ré-exécuter tout le pipeline d'indexation (extraction, nettoyage,
chunking) à chaque requête.

MODIFICATION (intégration corpus juridique) : sérialise désormais aussi
``chunk_id``, ``article``, ``page`` et ``section`` (ajoutés à
``ChunkDocument``, cf. ``chunking.py``). Un JSON déjà écrit par l'ancienne
version de ce module reste chargeable : ces clés sont simplement absentes
et ``.get(...)`` retombe sur ``None`` (valeur par défaut du champ).
"""

from __future__ import annotations

import json
from pathlib import Path

from backend.rag.chunking import ChunkDocument

CHEMIN_CHUNKS_PAR_DEFAUT = (
    Path(__file__).resolve().parents[2] / "data" / "chunks" / "corpus_chunks.json"
)


def sauvegarder_chunks(
    chunks: list[ChunkDocument], chemin: Path = CHEMIN_CHUNKS_PAR_DEFAUT
) -> None:
    """Sérialise les chunks du corpus en JSON."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    donnees = [
        {
            "document_titre": chunk.document_titre,
            "niveau": chunk.niveau,
            "type_source": chunk.type_source,
            "position": chunk.position,
            "texte": chunk.texte,
            "chunk_id": chunk.chunk_id,
            "article": chunk.article,
            "page": chunk.page,
            "section": chunk.section,
            "filename": chunk.filename,
        }
        for chunk in chunks
    ]
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")


def charger_chunks(chemin: Path = CHEMIN_CHUNKS_PAR_DEFAUT) -> list[ChunkDocument]:
    """Recharge les chunks du corpus depuis leur sérialisation JSON."""
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    return [
        ChunkDocument(
            document_titre=item["document_titre"],
            niveau=item["niveau"],
            type_source=item["type_source"],
            position=item["position"],
            texte=item["texte"],
            chunk_id=item.get("chunk_id"),
            article=item.get("article"),
            page=item.get("page"),
            section=item.get("section"),
            filename=item.get("filename"),
        )
        for item in donnees
    ]
