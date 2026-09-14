"""Pipeline RAG juridique - point d'entrée CLI.

Usage :

    python rag_pipeline.py "Quelles sont les activités qui donnent la qualité de commerçant au Maroc ?"

Flux :
    question
      -> recherche vectorielle (ChromaDB, embeddings E5 préfixés "query: ")
      -> recherche lexicale (BM25, sur data/chunks/corpus_chunks.json)
      -> fusion RRF (k=60)
      -> reranking (BAAI/bge-reranker-v2-m3, top 5-8)
      -> génération (Groq, réponse + citations article/page/document)

Suppose que ``scripts/importer_corpus_structurel.py`` puis
``scripts/build_index.py`` ont déjà été exécutés (corpus persisté et index
Chroma construit).
"""

from __future__ import annotations

import argparse
import sys

from backend.rag.chunk_store import charger_chunks
from backend.rag.embeddings import encoder_requete, obtenir_modele_embedding
from backend.rag.generation import ClientGroq, deduppliquer_citations, generer_reponse
from backend.rag.hybrid_search import fusionner_resultats
from backend.rag.indexing import IndexChromaDB
from backend.rag.lexical_search import IndexLexicalBM25
from backend.rag.reranking import obtenir_modele_reranker, reranker_score

NB_CANDIDATS_PAR_MOTEUR = 8  # aligné sur rag_service.py (réduit à nouveau, cf. commentaire)
NB_PASSAGES_FINAUX = 6  # aligné sur rag_service.py (NB_EXTRAITS_RETENUS)

# Score de confiance minimal (sigmoïde du score du reranker, dans [0, 1])
# pour considérer qu'un passage justifie un appel à Groq.
#
# Calibré sur 3 mesures réelles (peu, à affiner avec plus de cas) :
#   - "Obligations comptables du commerçant" (pertinente)      -> 0.730
#   - "Taux de TVA sur les jeux vidéo" (hors-sujet)             -> 0.501
#   - "Recette du tajine aux pruneaux" (hors-sujet total)       -> 0.500
# Les cas hors-sujet se regroupent près de 0.50 (logit brut proche de 0,
# donc sigmoïde proche de 0.5 — PAS proche de 0 comme un score de similarité
# cosinus le laisserait supposer). 0.60 se place entre les deux groupes
# observés. Le score du meilleur candidat est toujours affiché (stderr) :
# resserrer ce seuil avec d'autres mesures (plusieurs questions pertinentes
# ET hors-sujet) avant de le considérer comme fiable.
SEUIL_CONFIANCE_RERANKER = 0.60


def repondre(question: str) -> None:
    modele_embedding = obtenir_modele_embedding()
    index_vectoriel = IndexChromaDB()

    print("Chargement du corpus (BM25)...", file=sys.stderr)
    chunks = charger_chunks()
    index_lexical = IndexLexicalBM25(chunks)

    print("Recherche vectorielle + lexicale...", file=sys.stderr)
    vecteur_requete = encoder_requete(question, modele_embedding)
    resultats_semantiques = index_vectoriel.rechercher(vecteur_requete, NB_CANDIDATS_PAR_MOTEUR)
    resultats_lexicaux = index_lexical.rechercher(question, NB_CANDIDATS_PAR_MOTEUR)

    print("Fusion RRF...", file=sys.stderr)
    candidats = fusionner_resultats(resultats_semantiques, resultats_lexicaux)

    print("Reranking...", file=sys.stderr)
    modele_reranker = obtenir_modele_reranker()
    resultats_reranking = reranker_score(question, candidats, modele_reranker)

    meilleur_score = resultats_reranking[0].score if resultats_reranking else 0.0
    print(f"  meilleur score de confiance (reranker) : {meilleur_score:.3f}", file=sys.stderr)

    if not resultats_reranking or meilleur_score < SEUIL_CONFIANCE_RERANKER:
        print()
        print("=" * 80)
        print(f"QUESTION : {question}")
        print("=" * 80)
        print()
        print(
            "Cette question semble hors du périmètre du corpus juridique disponible "
            "(aucun passage suffisamment pertinent n'a été trouvé). Je ne peux pas y "
            "répondre de manière fiable à partir des documents indexés."
        )
        return

    passages_finaux = [item.resultat for item in resultats_reranking[:NB_PASSAGES_FINAUX]]

    print("Génération de la réponse (Groq)...", file=sys.stderr)
    client_llm = ClientGroq()
    reponse = generer_reponse(question, passages_finaux, client_llm)

    print()
    print("=" * 80)
    print(f"QUESTION : {question}")
    print("=" * 80)
    print()
    print(reponse.texte)
    print()
    print("-" * 80)
    print("SOURCES UTILISÉES :")
    print("-" * 80)
    # dédupliquées pour l'affichage : plusieurs extraits (sous-découpage
    # d'un même article, ou même guide cité deux fois) peuvent partager la
    # même référence — cf. deduppliquer_citations pour le détail.
    for citation in deduppliquer_citations(reponse.citations):
        print(f"  - {citation.reference}  ({citation.provenance})")


def main() -> None:
    parseur = argparse.ArgumentParser(description="Pipeline RAG juridique (Maroc)")
    parseur.add_argument("question", help="Question en langage naturel")
    arguments = parseur.parse_args()

    repondre(arguments.question)


if __name__ == "__main__":
    main()
