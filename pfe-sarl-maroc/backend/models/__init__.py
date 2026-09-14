"""Expose the shared declarative Base and every ORM model.

L'import de tous les modeles ici garantit deux choses :
1. Alembic (``alembic/env.py``) peut decouvrir l'integralite du schema via
   ``Base.metadata`` pour generer les migrations.
2. Les relations SQLAlchemy declarees avec des chaines (ex. ``list["Dossier"]``)
   se resolvent correctement, tous les modeles etant enregistres dans le meme
   registre au moment de leur premiere utilisation.
"""

from backend.core.database import Base
from backend.models.chat import CitationSource, Question, Reponse
from backend.models.corpus import Chunk, DocumentCorpus
from backend.models.dossier import Dossier
from backend.models.evaluation import Anomalie, Evaluation
from backend.models.identite_personne import IdentitePersonne
from backend.models.piece_justificative import PieceJustificative
from backend.models.utilisateur import Utilisateur

__all__ = [
    "Base",
    "Utilisateur",
    "Dossier",
    "IdentitePersonne",
    "PieceJustificative",
    "Evaluation",
    "Anomalie",
    "Question",
    "Reponse",
    "CitationSource",
    "DocumentCorpus",
    "Chunk",
]
