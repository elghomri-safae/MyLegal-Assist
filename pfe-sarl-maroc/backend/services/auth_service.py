"""Service d'inscription et d'authentification des utilisateurs (Phase 6)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.core.exceptions import AppError
from backend.core.security import (
    HASH_FACTICE_TEMPS_CONSTANT,
    creer_jeton_acces,
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)
from backend.repositories.utilisateur_repository import UtilisateurRepository
from backend.schemas.auth import (
    Token,
    UtilisateurConnexion,
    UtilisateurInscription,
    UtilisateurPublic,
)


class EmailDejaUtiliseError(AppError):
    """Levée quand l'email fourni à l'inscription est déjà utilisé."""


class IdentifiantsInvalidesError(AppError):
    """Levée quand l'email ou le mot de passe fourni à la connexion est incorrect."""


def _normaliser_email(email: str) -> str:
    """Normalise la casse d'un email avant toute comparaison ou écriture en base.

    La colonne ``email`` porte une contrainte ``unique=True`` en base, mais
    la comparaison SQL est sensible à la casse : sans normalisation,
    "Test@x.com" et "test@x.com" seraient acceptés comme deux comptes
    distincts (violation de fait de l'unicité attendue), et un utilisateur
    inscrit avec une casse donnée ne pourrait pas se reconnecter en tapant
    son email avec une casse différente. La partie locale d'un email est
    techniquement sensible à la casse au sens strict de la RFC 5321, mais en
    pratique aucun fournisseur grand public ou professionnel courant ne la
    traite ainsi ; la normaliser ici est le choix le plus sûr.
    """
    return email.strip().lower()


def inscrire_utilisateur(db: Session, payload: UtilisateurInscription) -> UtilisateurPublic:
    """Inscrit un nouvel utilisateur, en vérifiant l'unicité de l'email."""
    repository = UtilisateurRepository(db)
    email_normalise = _normaliser_email(payload.email)

    if repository.obtenir_par_email(email_normalise) is not None:
        raise EmailDejaUtiliseError(f"L'email {email_normalise} est déjà utilisé.")

    utilisateur = repository.creer(
        nom=payload.nom,
        email=email_normalise,
        role=payload.role.value,
        mot_de_passe_hash=hacher_mot_de_passe(payload.mot_de_passe),
    )

    return UtilisateurPublic(
        id=str(utilisateur.id),
        nom=utilisateur.nom,
        email=utilisateur.email,
        role=utilisateur.role,
    )


def authentifier_utilisateur(db: Session, payload: UtilisateurConnexion) -> Token:
    """Authentifie un utilisateur et retourne un jeton d'accès JWT.

    Le calcul PBKDF2 (``verifier_mot_de_passe``) est systématiquement exécuté,
    même quand l'email n'existe pas (contre un hash factice de référence) :
    sans cela, une réponse pour un email inexistant reviendrait quasi
    instantanément (aucun hachage effectué) alors qu'un email existant avec
    un mauvais mot de passe coûte ~260 000 itérations PBKDF2, ce qui permet
    d'énumérer les emails inscrits par simple mesure du temps de réponse,
    même si le message d'erreur renvoyé est identique dans les deux cas.
    """
    repository = UtilisateurRepository(db)
    utilisateur = repository.obtenir_par_email(_normaliser_email(payload.email))

    hash_a_verifier = (
        utilisateur.mot_de_passe_hash if utilisateur is not None else HASH_FACTICE_TEMPS_CONSTANT
    )
    mot_de_passe_correct = verifier_mot_de_passe(payload.mot_de_passe, hash_a_verifier)

    if utilisateur is None or not mot_de_passe_correct:
        raise IdentifiantsInvalidesError("Email ou mot de passe incorrect.")

    jeton = creer_jeton_acces(
        utilisateur_id=str(utilisateur.id), email=utilisateur.email, role=utilisateur.role
    )
    return Token(access_token=jeton)
