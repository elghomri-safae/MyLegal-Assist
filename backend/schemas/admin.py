"""Schémas Pydantic du module administration (lecture seule, admin uniquement).

``DossierAdminRead`` enveloppe ``DossierRead`` (inchangé) plutôt que d'en
dupliquer les champs : réutilise telle quelle la construction déjà faite par
``dossier_service._construire_dossier_read``, et ajoute seulement ce qui
manque pour une vue admin — savoir à QUEL client appartient le dossier
(``DossierRead`` ne porte aucune identité d'entrepreneur, cohérent avec son
usage normal où l'appelant est déjà cet entrepreneur).
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr

from backend.schemas.dossier import DossierRead


class DossierAdminRead(BaseModel):
    """Un dossier, vu par un administrateur : son contenu + l'identité du client."""

    dossier: DossierRead
    entrepreneur_nom: str
    entrepreneur_email: EmailStr
