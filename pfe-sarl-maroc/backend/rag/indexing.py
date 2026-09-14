"""Indexation et recherche vectorielle des chunks du corpus (ChromaDB).

Le moteur réel (ChromaDB — imposé par le cahier des charges) est encapsulé
derrière le protocole ``IndexVectoriel``, selon le même principe que les
autres dépendances lourdes du projet (import différé, substitution par un
index factice en test).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

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
            identifiant = f"chunk-{self._compteur}"
            self._compteur += 1
            self._collection.add(
                ids=[identifiant],
                embeddings=[list(vecteur)],
                documents=[chunk.texte],
                metadatas=[
                    {
                        "document_titre": chunk.document_titre,
                        "niveau": chunk.niveau,
                        "type_source": chunk.type_source,
                        "position": chunk.position,
                    }
                ],
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
            chunk = ChunkDocument(
                document_titre=metadata["document_titre"],
                niveau=metadata["niveau"],
                type_source=metadata["type_source"],
                position=metadata["position"],
                texte=texte,
            )
            resultats_convertis.append(
                ResultatRechercheSemantique(
                    identifiant=identifiant, chunk=chunk, score=1.0 - float(distance)
                )
            )
        return resultats_convertis
