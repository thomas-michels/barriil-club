from typing import List
from pydantic import BaseModel, Field, SerializeAsAny

from app.api.dependencies.pagination_parameters import Pagination


class MessageResponse(BaseModel):
    message: str = Field(example="Success")


class Response(MessageResponse):
    data: SerializeAsAny[BaseModel] | SerializeAsAny[List[BaseModel]] | None = Field()


class ListResponseSchema(Response):
    """
    Schema for ListResponseSchema
    """

    pagination: Pagination = Field()
    data: SerializeAsAny[BaseModel] | SerializeAsAny[List[BaseModel]] | None = Field()
