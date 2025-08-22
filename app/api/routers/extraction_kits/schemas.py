from typing import List

from pydantic import ConfigDict, Field

from app.api.shared_schemas.responses import Response
from app.crud.extraction_kits.schemas import (
    ExtractionKitInDB,
    ExtractionKitStatus,
    ExtractionKitType,
)

EXAMPLE_GAUGE = {
    "id": "pga_12345678",
    "brand": "Acme",
    "type": ExtractionKitType.SIMPLE,
    "serial_number": "SN123",
    "last_calibration_date": "2024-01-01",
    "status": ExtractionKitStatus.ACTIVE,
    "notes": "notes",
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class ExtractionKitResponse(Response):
    data: ExtractionKitInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Extraction kit processed with success",
                "data": EXAMPLE_GAUGE,
            }
        }
    )


class ExtractionKitListResponse(Response):
    data: List[ExtractionKitInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Extraction kits found with success",
                "data": [EXAMPLE_GAUGE],
            }
        }
    )
