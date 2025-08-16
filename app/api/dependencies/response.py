from typing import List

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.shared_schemas.responses import ListResponseSchema, MessageResponse, Response


def build_response(
    status_code: status, message: str, data: BaseModel | List[BaseModel] = None
) -> JSONResponse:
    if isinstance(data, int):
        raw_response = Response(message=message, data=None)
        raw_response.data = data

    elif data:
        raw_response = Response(message=message, data=data)

    else:
        raw_response = MessageResponse(message=message)

    return JSONResponse(
        content=jsonable_encoder(raw_response.model_dump(by_alias=True, exclude_none=True)),
        status_code=status_code
    )


def build_list_response(
    status_code: status, message: str, pagination: dict, data: BaseModel | List[BaseModel] = None
) -> JSONResponse:
    if data:
        raw_response = ListResponseSchema(
            message=message,
            pagination=pagination,
            data=data
        )

    else:
        raw_response = MessageResponse(message=message)

    return JSONResponse(
        content=jsonable_encoder(raw_response.model_dump(by_alias=True, exclude_none=True)),
        status_code=status_code
    )
