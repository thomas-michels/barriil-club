from typing import List
from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.beer_types.schemas import BeerTypeInDB

EXAMPLE_BEER_TYPE = {
    "id": "bty_12345678",
    "name": "Pale Ale",
    "producer": "Brew Co",
    "abv": 5.0,
    "ibu": 40.0,
    "description": "Tasty beer",
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class BeerTypeResponse(Response):
    data: BeerTypeInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Beer type processed with success", "data": EXAMPLE_BEER_TYPE}
        }
    )


class BeerTypeListResponse(Response):
    data: List[BeerTypeInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Beer types found with success",
                "data": [EXAMPLE_BEER_TYPE],
            }
        }
    )
