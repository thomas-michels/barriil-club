from typing import List
from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.pressure_gauges.schemas import (
    PressureGaugeInDB,
    PressureGaugeType,
    PressureGaugeStatus,
)

EXAMPLE_GAUGE = {
    "id": "pga_12345678",
    "brand": "Acme",
    "type": PressureGaugeType.ANALOG,
    "serial_number": "SN123",
    "last_calibration_date": "2024-01-01",
    "status": PressureGaugeStatus.ACTIVE,
    "notes": "notes",
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class PressureGaugeResponse(Response):
    data: PressureGaugeInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Pressure gauge processed with success",
                "data": EXAMPLE_GAUGE,
            }
        }
    )


class PressureGaugeListResponse(Response):
    data: List[PressureGaugeInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Pressure gauges found with success",
                "data": [EXAMPLE_GAUGE],
            }
        }
    )
