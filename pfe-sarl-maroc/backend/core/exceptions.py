"""Custom application exceptions.

Ces exceptions traduisent en code deux des regles absolues du cahier des
charges : ne jamais inventer d'information juridique (voir
``CorpusInformationMissingError``) et garder toute decision tracable a une
regle documentee (voir ``RuleEvaluationError``).
"""


class AppError(Exception):
    """Base class for all application-specific errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CorpusInformationMissingError(AppError):
    """Levee quand une reponse juridique ne peut pas etre ancree dans le corpus.

    Le systeme doit signaler explicitement l'absence d'information plutot que
    de produire une reponse non tracable a une source (Regle absolue n8).
    """


class RuleEvaluationError(AppError):
    """Levee quand une regle du systeme expert ne peut pas etre evaluee.

    Par exemple si une donnee necessaire a la condition de la regle est
    absente du dossier soumis.
    """


class DossierIntrouvableError(AppError):
    """Levee quand un dossier n'existe pas ou n'appartient pas a l'utilisateur.

    Le meme message est utilise dans les deux cas (dossier inexistant ou
    appartenant a un autre entrepreneur) pour ne jamais reveler par la
    reponse HTTP l'existence d'un dossier appartenant a quelqu'un d'autre.
    """
