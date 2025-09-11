
class InvalidPassword(Exception):
    """
    Raised when password is invalid
    """

    def __init__(self, message="Senha inválida") -> None:
        self.message = message


class UnprocessableEntity(Exception):
    """
    Raised when there are some problem in entity
    """

    def __init__(self, message="Entidade não processável") -> None:
        self.message = message


class NotFoundError(Exception):
    """
    Raised when something not found
    """

    def __init__(self, message="Não encontrado") -> None:
        self.message = message


class BadRequestError(Exception):
    """Raised when a request cannot be processed"""

    def __init__(self, message="Requisição inválida") -> None:
        self.message = message
