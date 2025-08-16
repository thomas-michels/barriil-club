"""
    Module for pagination_parameters
"""
from pydantic import Field
from app.core.models.base_schema import GenericModel


class Links(GenericModel):
    previous: str | None = Field(default=None, example="/health")
    self: str = Field(example="/health")
    next: str | None = Field(default=None, example="/health")


class Pagination(GenericModel):
    total: int = Field(example=123)
    page_size: int = Field(example=123)
    pages: int = Field(example=123)
    page: int = Field(example=123)
    links: Links


async def pagination_parameters(page: int = 1, pageSize: int = 15):
    page_size = max(1, pageSize)
    page = max(1, page)

    return {"page": page, "page_size": page_size}
