from typing import List
from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.kegs.schemas import KegInDB, KegStatus

EXAMPLE_KEG = {
    "id": "keg_12345678",
    "number": "1",
    "size_l": 50,
    "beer_type_id": "bty_123",
    "cost_price_per_l": 5.5,
    "sale_price_per_l": 8.0,
    "lot": "L001",
    "expiration_date": "2025-01-01",
    "current_volume_l": 25,
    "status": KegStatus.AVAILABLE,
    "notes": "notes",
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class KegResponse(Response):
    data: KegInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Keg processed with success", "data": EXAMPLE_KEG}
        }
    )


class KegListResponse(Response):
    data: List[KegInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Kegs found with success",
                "data": [EXAMPLE_KEG],
            }
        }
    )
