from typing import List

from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.extractors.schemas import ExtractorInDB

EXAMPLE_EXTRACTOR = {
    "id": "ext_12345678",
    "brand": "Acme",
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class ExtractorResponse(Response):
    data: ExtractorInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Extractor processed with success", "data": EXAMPLE_EXTRACTOR}
        }
    )


class ExtractorListResponse(Response):
    data: List[ExtractorInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Extractors found with success",
                "data": [EXAMPLE_EXTRACTOR],
            }
        }
    )
