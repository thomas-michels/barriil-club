from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.shared_schemas.responses import MessageResponse
from app.core.exceptions import (
    InvalidPassword,
    NotFoundError,
    UnprocessableEntity,
)
from app.core.configs import get_logger

_logger = get_logger(__name__)


def http_exception_handler(request: Request, exc: HTTPException):
    error = MessageResponse(message=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error.model_dump()),
    )


def unprocessable_entity_error_422(request: Request, exc: UnprocessableEntity):
    error = MessageResponse(message=exc.message)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(error.model_dump()),
    )


def not_found_error_404(request: Request, exc: NotFoundError):
    error = MessageResponse(message=exc.message)

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(error.model_dump()),
    )


def generic_error_400(request: Request, exc: InvalidPassword):
    error = MessageResponse(message=exc.message)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(error.model_dump()),
    )


def generic_error_500(request: Request, exc: Exception):
    """Internal error"""
    if hasattr(exc, "detail"):
        error = MessageResponse(message=exc.detail)
        status_code = exc.status_code

    else:
        _logger.error(f"Internal error - {str(exc)} - URL: {request.url.path}")
        error = MessageResponse(message="An unexpected error happen")
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(error.model_dump()),
    )
