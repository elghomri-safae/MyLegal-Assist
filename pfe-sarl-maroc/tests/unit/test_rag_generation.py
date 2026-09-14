"""Test unitaire de la génération de réponse (backend/rag/generation.py).

Le client Groq réel n'est pas exercé (dépendance externe + réseau non
disponible dans ce sandbox) ; ce test substitue un client factice
respectant l'interface ``ClientLLM``.
"""

from backend.rag.chunking import ChunkDocument
from backend.rag.generation import construire_prompt_utilisateur, generer_reponse
from backend.rag.hybrid_search import ResultatRechercheHybride


class _ClientFactice:
    def __init__(self, texte_reponse: str) -> None:
        self._texte_reponse = texte_reponse

    def generer(self, prompt_systeme: str, prompt_utilisateur: str) -> str:
        return self._texte_reponse


def _extrait(
    document_titre: str, niveau: int, position: int, texte: str
) -> ResultatRechercheHybride:
    chunk = ChunkDocument(
        document_titre=document_titre,
        niveau=niveau,
        type_source="x",
        position=position,
        texte=texte,
    )
    return ResultatRechercheHybride(
        chunk=chunk, score_fusion=1.0, score_semantique=1.0, score_lexical=1.0
    )


def test_construire_prompt_utilisateur_inclut_la_question_et_les_extraits() -> None:
    """Le prompt utilisateur doit contenir la question et le texte de chaque extrait."""
    extraits = [_extrait("Loi 5-96", 1, 0, "Le capital minimum est fixe librement.")]

    prompt = construire_prompt_utilisateur("Quel est le capital minimum ?", extraits)

    assert "Quel est le capital minimum ?" in prompt
    assert "Le capital minimum est fixe librement." in prompt
    assert "Loi 5-96" in prompt


def test_generer_reponse_retourne_les_extraits_fournis_comme_citations() -> None:
    """Les citations retournées doivent correspondre exactement aux extraits fournis."""
    extraits = [
        _extrait("Loi 5-96", 1, 0, "Extrait A"),
        _extrait("OMPIC", 2, 3, "Extrait B"),
    ]
    client = _ClientFactice("Reponse generee par le modele.")

    resultat = generer_reponse("Question test", extraits, client)

    assert resultat.texte == "Reponse generee par le modele."
    assert len(resultat.citations) == 2
    assert resultat.citations[0].document == "Loi 5-96"
    assert resultat.citations[0].niveau == 1
    assert resultat.citations[1].document == "OMPIC"
