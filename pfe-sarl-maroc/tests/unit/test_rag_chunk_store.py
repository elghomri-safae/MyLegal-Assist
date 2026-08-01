"""Test unitaire de la sérialisation des chunks (backend/rag/chunk_store.py)."""

from pathlib import Path

from backend.rag.chunk_store import charger_chunks, sauvegarder_chunks
from backend.rag.chunking import ChunkDocument


def test_sauvegarder_puis_charger_chunks_est_idempotent(tmp_path: Path) -> None:
    """Un cycle sauvegarde -> chargement doit restituer des chunks identiques."""
    chunks = [
        ChunkDocument(
            document_titre="Doc Test",
            niveau=1,
            type_source="texte_de_loi",
            position=0,
            texte="Extrait de test.",
        )
    ]
    chemin = tmp_path / "chunks.json"

    sauvegarder_chunks(chunks, chemin=chemin)
    chunks_recharges = charger_chunks(chemin=chemin)

    assert chunks_recharges == chunks
