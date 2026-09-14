"""Génération de la réponse finale (Groq API) avec citations tracables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.config.settings import get_settings
from backend.rag.corpus_loader import provenance_pour_filename
from backend.rag.hybrid_search import ResultatRechercheHybride
TEMPERATURE_GENERATION = 0.1  # faible : privilégie la cohérence factuelle sur la créativité
MAX_TOKENS_GENERATION = 700   # borne la longueur de réponse


MODELE_GROQ_PAR_DEFAUT = "openai/gpt-oss-120b"

INSTRUCTION_SYSTEME = (
    "Tu es un assistant juridique specialise dans la creation et la gestion "
    "d'entreprises au Maroc (SARL, SA, auto-entrepreneur, formalites "
    "OMPIC/CNSS/fiscales). Reponds UNIQUEMENT a partir des extraits de sources "
    "fournis ci-dessous, sans jamais inventer de disposition juridique. "
    "Pour chaque affirmation, cite la source entre crochets exactement au "
    "format indique devant chaque extrait (ex. [Code de commerce marocain, "
    "Article 6, p.2]). Si les extraits fournis ne permettent pas de repondre "
    "a la question, dis-le explicitement plutot que d'inventer une reponse."
)


def _reference_citation(chunk) -> str:
    """
    Construit le libellé de référence avec un format UNIFORME.
    - Document + Article + p.X (si page disponible)
    - Le format est toujours "Document, Article, p.X"
    """
    parties = [chunk.document_titre]
    if chunk.article:
        parties.append(chunk.article)
    if chunk.page is not None:
        # Uniformisation : toujours "p.X" avec un point
        parties.append(f"p.{chunk.page}")
    return ", ".join(parties)


@dataclass(frozen=True)
class Citation:
    document: str
    article: str | None
    page: int | None
    chunk_id: str | None
    reference: str
    provenance: str


@dataclass(frozen=True)
class ReponseGeneree:
    texte: str
    citations: list[Citation]


class ClientLLM(Protocol):
    def generer(
        self,
        prompt_systeme: str,
        prompt_utilisateur: str,
        temperature: float = TEMPERATURE_GENERATION,
        max_tokens: int = MAX_TOKENS_GENERATION,
    ) -> str:
        ...



class ClientGroq:
    def __init__(self, modele: str = MODELE_GROQ_PAR_DEFAUT) -> None:
        from groq import Groq
        parametres = get_settings()
        self._client = Groq(api_key=parametres.groq_api_key)
        self._modele = modele

    def generer(
        self,
        prompt_systeme: str,
        prompt_utilisateur: str,
        temperature: float = TEMPERATURE_GENERATION,
        max_tokens: int = MAX_TOKENS_GENERATION,
    ) -> str:
        reponse = self._client.chat.completions.create(
            model=self._modele,
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": prompt_utilisateur},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return reponse.choices[0].message.content or ""

    def generer_avec_diagnostic(
        self,
        prompt_systeme: str,
        prompt_utilisateur: str,
        temperature: float = TEMPERATURE_GENERATION,
        max_tokens: int = MAX_TOKENS_GENERATION,
    ) -> tuple[str, bool, int]:
        """Comme generer(), mais retourne en plus un indicateur de complétude
        et le nombre de tokens réellement consommés, à des fins de test/calibration.
        finish_reason == "stop" signifie que le modèle a terminé naturellement ;
        "length" signifie que la réponse a été tronquée par max_tokens."""
        reponse = self._client.chat.completions.create(
            model=self._modele,
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": prompt_utilisateur},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choix = reponse.choices[0]
        complete = choix.finish_reason == "stop"
        nb_tokens = reponse.usage.completion_tokens if reponse.usage else 0
        return choix.message.content or "", complete, nb_tokens
    


def construire_prompt_utilisateur(question: str, extraits: list[ResultatRechercheHybride]) -> str:
    blocs_extraits = "\n\n".join(
        f"[{_reference_citation(resultat.chunk)}]\n{resultat.chunk.texte}"
        for resultat in extraits
    )
    return f"Extraits de sources :\n\n{blocs_extraits}\n\nQuestion : {question}"




def deduppliquer_citations(citations: list[Citation]) -> list[Citation]:
    """
    Déduplique les citations en se basant sur : document + page.
    Cela évite les doublons même si le format de page diffère (p.4 vs 4).
    """
    vues: set[str] = set()
    resultat: list[Citation] = []
    for citation in citations:
        # Clé unique : document + page (sans le "p." pour ignorer les différences de format)
        cle = f"{citation.document}|{citation.page}" if citation.page is not None else citation.document
        if cle in vues:
            continue
        vues.add(cle)
        resultat.append(citation)
    return resultat


def generer_reponse(
    question: str, extraits: list[ResultatRechercheHybride], client: ClientLLM
) -> ReponseGeneree:
    prompt_utilisateur = construire_prompt_utilisateur(question, extraits)
    texte = client.generer(INSTRUCTION_SYSTEME, prompt_utilisateur)

    citations: list[Citation] = []
    for resultat in extraits:
        # Récupérer la provenance
        provenance = provenance_pour_filename(resultat.chunk.filename)
        
        # Si inconnue, utiliser le titre du document (correction du "Source non renseignée")
        if provenance == "Source non renseignée" and resultat.chunk.document_titre:
            provenance = resultat.chunk.document_titre

        citations.append(
            Citation(
                document=resultat.chunk.document_titre,
                article=resultat.chunk.article,
                page=resultat.chunk.page,
                chunk_id=resultat.chunk.chunk_id,
                reference=_reference_citation(resultat.chunk),
                provenance=provenance,
            )
        )

    return ReponseGeneree(texte=texte, citations=citations)




