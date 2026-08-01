"""Génération de la réponse finale (Groq API) avec citations tracables.

Le client réel (Groq) est encapsulé derrière le protocole ``ClientLLM``
(import différé, substitution par un client factice en test — le réseau de
ce sandbox ne permet de toute façon pas d'appeler l'API Groq réelle, voir
ARCHITECTURE.md §12).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.config.settings import get_settings
from backend.rag.hybrid_search import ResultatRechercheHybride

MODELE_GROQ_PAR_DEFAUT = "llama-3.3-70b-versatile"

INSTRUCTION_SYSTEME = (
    "Tu es un assistant juridique specialise dans la creation de SARL et SARL AU au "
    "Maroc. Reponds UNIQUEMENT a partir des extraits de sources fournis ci-dessous. "
    "Pour chaque affirmation, cite la source entre crochets au format "
    "[Titre du document, Niveau N]. Si les extraits fournis ne permettent pas de "
    "repondre a la question, dis-le explicitement plutot que d'inventer une reponse."
)


@dataclass(frozen=True)
class Citation:
    """Une source citée dans la réponse générée."""

    document: str
    niveau: int
    reference: str


@dataclass(frozen=True)
class ReponseGeneree:
    """La réponse produite par le LLM, avec ses citations."""

    texte: str
    citations: list[Citation]


class ClientLLM(Protocol):
    """Interface minimale attendue d'un client LLM générateur de texte."""

    def generer(self, prompt_systeme: str, prompt_utilisateur: str) -> str:
        """Retourne le texte généré par le modèle pour le prompt fourni."""
        ...


class ClientGroq:
    """Adaptateur Groq implémentant ``ClientLLM``."""

    def __init__(self, modele: str = MODELE_GROQ_PAR_DEFAUT) -> None:
        from groq import Groq  # import différé

        parametres = get_settings()
        self._client = Groq(api_key=parametres.groq_api_key)
        self._modele = modele

    def generer(self, prompt_systeme: str, prompt_utilisateur: str) -> str:
        reponse = self._client.chat.completions.create(
            model=self._modele,
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": prompt_utilisateur},
            ],
        )
        return reponse.choices[0].message.content or ""


def construire_prompt_utilisateur(question: str, extraits: list[ResultatRechercheHybride]) -> str:
    """Construit le prompt utilisateur incluant la question et les extraits sélectionnés."""
    blocs_extraits = "\n\n".join(
        f"[{resultat.chunk.document_titre}, Niveau {resultat.chunk.niveau}]\n"
        f"{resultat.chunk.texte}"
        for resultat in extraits
    )
    return f"Extraits de sources :\n\n{blocs_extraits}\n\nQuestion : {question}"


def generer_reponse(
    question: str, extraits: list[ResultatRechercheHybride], client: ClientLLM
) -> ReponseGeneree:
    """Génère la réponse finale.

    Les citations retournées correspondent exactement aux extraits fournis
    en contexte au LLM (traçabilité garantie par construction), plutôt
    qu'une extraction par expression régulière du texte généré, qui serait
    fragile et moins fiable (Règle absolue n°7).
    """
    prompt_utilisateur = construire_prompt_utilisateur(question, extraits)
    texte = client.generer(INSTRUCTION_SYSTEME, prompt_utilisateur)

    citations = [
        Citation(
            document=resultat.chunk.document_titre,
            niveau=resultat.chunk.niveau,
            reference=f"extrait n°{resultat.chunk.position}",
        )
        for resultat in extraits
    ]
    return ReponseGeneree(texte=texte, citations=citations)
