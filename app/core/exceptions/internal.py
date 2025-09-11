
class InternalErrorException(Exception):
    """
    Raised when an internal error happened
    """

    def __init__(self, message="Erro interno") -> None:
        self.message = message
