from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requer autenticação"
        )


class InternalErrorException(HTTPException):
    def __init__(self, detail: str = None) -> None:
        if not detail:
            detail = "Ocorreu um erro inesperado"

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class UnprocessableEntityException(HTTPException):
    def __init__(self, detail: str = None) -> None:
        if not detail:
            detail = "Entidade não processável"

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class BadRequestException(HTTPException):
    def __init__(self, detail: str = None) -> None:
        if not detail:
            detail = "Requisição inválida"

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )


class TooManyRequestException(HTTPException):
    def __init__(self, detail: str = None) -> None:
        if not detail:
            detail = "Muitas requisições"

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail
        )


class PaymentRequiredException(HTTPException):
    def __init__(self, detail: str = None) -> None:
        if not detail:
            detail = "Pagamento necessário"

        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail
        )
