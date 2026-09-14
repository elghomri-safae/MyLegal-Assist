
"""Indexation et recherche vectorielle des chunks du corpus (ChromaDB).

Le moteur réel (ChromaDB — imposé par le cahier des charges) est encapsulé
derrière le protocole ``IndexVectoriel``, selon le même principe que les
autres dépendances lourdes du projet (import différé, substitution par un
index factice en test).

MODIFICATION (intégration corpus juridique) :
- les métadonnées Chroma incluent désormais ``article``, ``page`` et
  ``section`` (nécessaires pour que ``generation.py`` puisse citer article +
  page + document source) ;
- ``chunk.chunk_id`` (stable et déterministe, cf. ``corpus_loader.py``) est
  utilisé comme identifiant Chroma quand il est disponible, plutôt qu'un
  compteur interne : réindexer le même corpus produit les mêmes ID
  (``ajouter`` devient idempotent — un réimport ne duplique pas les
  chunks), au lieu de dépendre de l'ordre d'exécution du process ;
- ChromaDB rejette les valeurs ``None`` dans les métadonnées : les champs
  optionnels absents (``niveau``, ``article``, ``page``, ``section``) sont
  omis de la métadonnée stockée plutôt que convertis en valeur factice, et
  ``rechercher`` les reconstruit à ``None`` via ``.get(...)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from backend.config.settings import get_settings
from backend.rag.chunking import ChunkDocument
from backend.rag.embeddings import Vecteur


@dataclass(frozen=True)
class ResultatRechercheSemantique:
    """Un résultat de recherche vectorielle, avec son score de similarité."""

    identifiant: str
    chunk: ChunkDocument
    score: float


class IndexVectoriel(Protocol):
    """Interface minimale attendue d'un index vectoriel."""

    def ajouter(self, chunks: list[ChunkDocument], vecteurs: list[Vecteur]) -> list[str]:
        """Ajoute des chunks (et leurs vecteurs) à l'index, retourne leurs identifiants."""
        ...

    def rechercher(self, vecteur_requete: Vecteur, k: int) -> list[ResultatRechercheSemantique]:
        """Retourne les k chunks les plus proches du vecteur de requête."""
        ...


def _identifiant_chunk(chunk: ChunkDocument, compteur_repli: int) -> str:
   
    return chunk.chunk_id if chunk.chunk_id is not None else f"chunk-{compteur_repli}"

# Les chunk_id sont générés par ton script de chunking (ex: LOI-N°-5-96__p7__art7). 
# Si tu réindexes le corpus, ces IDs restent les mêmes.
# Comparaison : Sans IDs stables (si on utilisait un compteur aléatoire), 
# réindexer le corpus créerait de nouveaux IDs à chaque fois.
#  Tu aurais des doublons dans ChromaDB et tu perdrais la traçabilité.

def _metadata_vers_chroma(chunk: ChunkDocument) -> dict[str, Any]:
    """Construit la métadonnée Chroma en omettant les champs à ``None``
    (Chroma rejette ``None`` comme valeur de métadonnée)."""
    metadata: dict[str, Any] = {
        "document_titre": chunk.document_titre,
        "type_source": chunk.type_source,
        "position": chunk.position,
    }
    if chunk.niveau is not None:
        metadata["niveau"] = chunk.niveau
    if chunk.article is not None:
        metadata["article"] = chunk.article
    if chunk.page is not None:
        metadata["page"] = chunk.page
    if chunk.section is not None:
        metadata["section"] = chunk.section
    if chunk.filename is not None:
        metadata["filename"] = chunk.filename
    return metadata


def _chunk_depuis_metadata(identifiant: str, texte: str, metadata: dict[str, Any]) -> ChunkDocument:
    return ChunkDocument(
        document_titre=metadata["document_titre"],
        type_source=metadata["type_source"],
        position=metadata["position"],
        texte=texte,
        niveau=metadata.get("niveau"),
        chunk_id=identifiant,
        article=metadata.get("article"),
        page=metadata.get("page"),
        section=metadata.get("section"),
        filename=metadata.get("filename"),
    )


class IndexChromaDB:
    """Adaptateur ChromaDB implémentant ``IndexVectoriel``."""

    def __init__(self, nom_collection: str = "corpus_juridique") -> None:
        import chromadb  # import différé : dépendance non exercée dans ce sandbox

        parametres = get_settings()
        self._client = chromadb.PersistentClient(path=parametres.chroma_persist_directory)
        # Metrique explicitement fixee a "cosine" : les embeddings produits par
        # ModeleSentenceTransformer sont normalises (normalize_embeddings=True),
        # et le score retourne par rechercher() (1.0 - distance) n'est une
        # similarite cosinus valide que sous cette metrique. Sans ce parametre,
        # ChromaDB utilise "l2" par defaut : le classement reste correct par
        # coincidence (l2^2 est une fonction decroissante de la similarite
        # cosinus pour des vecteurs normalises), mais la valeur du score serait
        # fausse si elle etait un jour affichee ou seuillee.
        self._collection = self._client.get_or_create_collection(
            nom_collection, metadata={"hnsw:space": "cosine"}
        )
        self._compteur = 0

    def ajouter(self, chunks: list[ChunkDocument], vecteurs: list[Vecteur]) -> list[str]:
        identifiants: list[str] = []
        for chunk, vecteur in zip(chunks, vecteurs, strict=True):
            identifiant = _identifiant_chunk(chunk, self._compteur)
            self._compteur += 1
            # add : ajoute un nouveau chunk. Si le chunk existe déjà, une erreur est levée.
            # upsert : si le chunk existe, il est mis à jour ; sinon, il est ajouté.
            # Comparaison : Sans upsert, tu devrais supprimer toute la collection avant de réindexer
            # (risque de perte de données). Avec upsert, c'est idempotent (on peut réindexer sans risque).
            # ``upsert`` plutôt que ``add`` : avec un chunk_id stable, relancer
            # l'indexation sur un corpus déjà indexé met à jour plutôt que de
            # dupliquer les entrées existantes.
            self._collection.upsert(
                ids=[identifiant],
                embeddings=[list(vecteur)],
                documents=[chunk.texte],
                metadatas=[_metadata_vers_chroma(chunk)],
            )
            identifiants.append(identifiant)
        return identifiants

    def rechercher(self, vecteur_requete: Vecteur, k: int) -> list[ResultatRechercheSemantique]:
        resultats = self._collection.query(query_embeddings=[list(vecteur_requete)], n_results=k)
        resultats_convertis: list[ResultatRechercheSemantique] = []
        for identifiant, texte, metadata, distance in zip(
            resultats["ids"][0],
            resultats["documents"][0],
            resultats["metadatas"][0],
            resultats["distances"][0],
            strict=True,
        ):
            chunk = _chunk_depuis_metadata(identifiant, texte, metadata)
            resultats_convertis.append(
                ResultatRechercheSemantique(
                    identifiant=identifiant, chunk=chunk, score=1.0 - float(distance)
                )
            )
        return resultats_convertis
