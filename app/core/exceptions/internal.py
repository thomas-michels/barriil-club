
class InternalErrorException(Exception):
    """
    Raised when an internal error happened
    """

    def __init__(self, message="Internal Error") -> None:
        self.message = message
