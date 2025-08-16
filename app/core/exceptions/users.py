
class InvalidPassword(Exception):
    """
    Raised when password is invalid
    """

    def __init__(self, message="Password is invalid") -> None:
        self.message = message


class UnprocessableEntity(Exception):
    """
    Raised when there are some problem in entity
    """

    def __init__(self, message="Unprocessable entity") -> None:
        self.message = message


class NotFoundError(Exception):
    """
    Raised when something not found
    """

    def __init__(self, message="Not found") -> None:
        self.message = message
