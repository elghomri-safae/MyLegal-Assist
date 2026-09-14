"""Import du corpus juridique structurel (chunking article-first externe)
vers le modèle ``ChunkDocument`` utilisé par le reste du pipeline RAG.

Le chunking du corpus n'est PAS effectué ici : il a déjà été fait en amont
(script de chunking structurel hybride, hors de ce backend — un article de
loi = une unité de découpage, sous-découpé seulement si trop long). Ce
module se contente de lire le JSON produit et de le convertir au format
``ChunkDocument`` attendu par ``indexing.py``, ``lexical_search.py``,
``hybrid_search.py``, etc.

DÉCISION (validée) : le nouveau corpus est la source de vérité et ne porte
pas de hiérarchie ``niveau`` (seul ``type_source`` y figure). Aucune
hiérarchie n'est déduite ici : ``niveau`` reste ``None`` pour tous les
chunks importés depuis ce corpus. Le retrieval/reranking/génération
s'appuient uniquement sur ``chunk_id``, ``filename``, ``document_titre``,
``page``, ``article``, ``section`` et ``type_source``.

CORRECTIF (traçabilité + provenance) : ``filename`` (nom de fichier brut,
ex. ``"Loi-n°-17-95-relative-aux-societes-anonymes-Aout-2021.pdf"``) est
maintenant conservé tel quel dans ``ChunkDocument.filename``, séparément de
``document_titre`` (le titre lisible affiché à l'utilisateur). Les deux
servent des usages différents : ``filename`` pour la traçabilité technique
exacte, ``document_titre``/``PROVENANCES`` pour l'affichage humain.

``TITRES_LISIBLES`` et ``PROVENANCES`` ne couvrent QUE les 8 documents
confirmés du corpus. Pour tout autre document (aucun ne devrait exister
selon la confirmation reçue — si un titre inattendu apparaît malgré tout à
l'affichage, cela signale un ``data/chunks/corpus_chunks.json`` obsolète ou
un corpus source contenant plus de documents que prévu, à vérifier), le
titre est dérivé automatiquement (``_titre_depuis_filename``) et la
provenance affichée est "Source non renseignée" — aucune provenance n'est
devinée.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from backend.rag.chunking import ChunkDocument

# Titres lisibles pour les 8 documents confirmés du corpus (override
# manuel, prioritaire sur la dérivation automatique). Tout document absent
# d'ici passe par ``_titre_depuis_filename``.
TITRES_LISIBLES: dict[str, str] = {
    "code de commerce marocain-1-15.pdf": "Code de commerce marocain",
    "Loi-n°-17-95-relative-aux-societes-anonymes-Aout-2021.pdf": ("Loi n° 17-95 relative aux sociétés anonymes — Août 2021"),
    "LOI-N°-5-96-Aout-2021.pdf": ("Loi n° 5-96 relative à la société en nom collectif, en commandite, " "à la SARL et à la société en participation — Août 2021"),
    "Loi_114-13_auto-entrepreneur.pdf": ("Loi n° 114-13 relative au statut de l'auto-entrepreneur"),
    "Loi_88-17_creation_entreprises_electronique.pdf": ("Loi n° 88-17 relative à la création des entreprises par voie électronique"),
    "Création et vie de l'entreprise.pdf": "Guide OMPIC — Création et vie de l'entreprise",
    (
        "Guide_d_utilisation_du_parcours_Affiliation_a_la_CNSS_and_Adhesion_a_"
        "Damancom_version_web_b6f440ddb6_1.pdf"
    ): "Guide CNSS — Affiliation et adhésion à Damancom",
    "TP+VF.pdf": "Document fiscal — Taxe professionnelle",
}

# Provenance des 8 documents confirmés du corpus, telle que fournie
# explicitement. AUCUNE provenance n'est devinée pour un document absent de
# cette table : ``PROVENANCE_PAR_DEFAUT`` s'applique alors.
PROVENANCES: dict[str, str] = {
    "code de commerce marocain-1-15.pdf": "Texte légal marocain — Loi n° 15-95",
    "Création et vie de l'entreprise.pdf": "OMPIC",
    (
        "Guide_d_utilisation_du_parcours_Affiliation_a_la_CNSS_and_Adhesion_a_"
        "Damancom_version_web_b6f440ddb6_1.pdf"
    ): "CNSS",
    "Loi-n°-17-95-relative-aux-societes-anonymes-Aout-2021.pdf": (
        "Texte légal marocain — Loi n° 17-95"
    ),
    "LOI-N°-5-96-Aout-2021.pdf": "Texte légal marocain — Loi n° 5-96",
    "Loi_114-13_auto-entrepreneur.pdf": "Texte légal marocain — Loi n° 114-13",
    "Loi_88-17_creation_entreprises_electronique.pdf": "Texte légal marocain — Loi n° 88-17",
    "TP+VF.pdf": "Direction Générale des Impôts (DGI) — Taxe professionnelle",
}
PROVENANCE_PAR_DEFAUT = "Source non renseignée"

# Mots courts / acronymes qu'on ne veut pas "Titre-caser" en un seul
# caractère majuscule + reste minuscule (ils sont déjà corrects tels quels).
_LONGUEUR_MOT_NON_CAPITALISE = 3


def _titre_depuis_filename(filename: str) -> str:
    """Dérive un titre lisible à partir d'un nom de fichier, sans dépendre
    d'un dictionnaire figé. Ne sert que de repli pour un document qui ne
    serait pas dans ``TITRES_LISIBLES`` (aucun n'est attendu, cf. note de
    module).

    Extension retirée par manipulation de chaîne (``rsplit``), PAS par
    ``pathlib.Path.stem`` : un nom de fichier contenant un ``/`` ferait
    perdre tout ce qui précède le ``/`` avec ``Path.stem``, qui le traite
    comme un séparateur de dossier.
    """
    nom = filename.rsplit(".", 1)[0] if "." in filename else filename
    nom = nom.replace("_", " ")
    nom = re.sub(r"(?<!\d)-(?!\d)", " ", nom)
    nom = re.sub(r"\s+", " ", nom).strip()

    mots = []
    for mot in nom.split(" "):
        if mot.isupper() or any(caractere.isdigit() for caractere in mot):
            mots.append(mot)
        elif len(mot) <= _LONGUEUR_MOT_NON_CAPITALISE:
            mots.append(mot)
        else:
            mots.append(mot[:1].upper() + mot[1:])
    return " ".join(mots)


def _titre_lisible(filename: str) -> str:
    if filename in TITRES_LISIBLES:
        return TITRES_LISIBLES[filename]
    return _titre_depuis_filename(filename)


def provenance_pour_filename(filename: str | None) -> str:
    """Provenance affichable d'un document, ou ``PROVENANCE_PAR_DEFAUT`` si
    inconnue. Ne devine jamais : seule la table ``PROVENANCES`` fait foi."""
    if filename is None:
        return PROVENANCE_PAR_DEFAUT
    return PROVENANCES.get(filename, PROVENANCE_PAR_DEFAUT)


def charger_corpus_structurel(chemin: Path) -> list[ChunkDocument]:
    """Lit le JSON du chunking structurel et le convertit en ``ChunkDocument``.

    ``niveau`` n'est PAS renseigné (reste ``None``) : aucune hiérarchie
    artificielle n'est introduite depuis ``type_source``.

    ``filename`` (nom de fichier brut) est conservé tel quel pour la
    traçabilité technique, séparément de ``document_titre`` (titre lisible).

    ``position`` est réattribué comme un index séquentiel PAR DOCUMENT
    (0, 1, 2, ...) : le corpus source ne porte pas de position entière
    (l'unité naturelle y est l'article, pas un numéro de position), mais
    ``hybrid_search.py`` utilise ``(document_titre, position)`` comme clé de
    dédoublonnage — cet index reconstruit satisfait ce contrat sans y
    toucher.
    """
    donnees = json.loads(chemin.read_text(encoding="utf-8"))

    compteurs_position: dict[str, int] = {}
    chunks: list[ChunkDocument] = []

    for item in donnees["chunks"]:
        metadata = item["metadata"]
        filename = metadata["filename"]

        position = compteurs_position.get(filename, 0)
        compteurs_position[filename] = position + 1

        chunks.append(
            ChunkDocument(
                document_titre=_titre_lisible(filename),
                type_source=metadata["type_source"],
                position=position,
                texte=item["text"],
                niveau=None,
                chunk_id=item["chunk_id"],
                article=metadata.get("article"),
                page=metadata.get("page"),
                section=metadata.get("section"),
                filename=filename,
            )
        )

    return chunks

# --- Validation d'intégrité applicative (remplace une FK impossible : les
# tables SQL documents_corpus/chunks ne sont jamais peuplées, le corpus
# réel vit dans ChromaDB + ce module) ---
DOCUMENTS_CONNUS: frozenset[str] = frozenset(TITRES_LISIBLES.values())




# Le dictionnaire TITRES_LISIBLES est juste le mécanisme qui produit document_titre à partir de filename. 
# Ce n'est pas un 3ème concept séparé — "titre lisible" est document_titre, ce sont juste deux façons 
# de nommer la même chose (le nom du dictionnaire vient du fait qu'il contient des titres lisibles).
