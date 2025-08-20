from typing import List
from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.beer_dispensers.schemas import BeerDispenserInDB, DispenserStatus, Voltage

EXAMPLE_DISPENSER = {
    "id": "bsd_12345678",
    "brand": "Acme",
    "model": "X1",
    "serial_number": "SN123",
    "taps_count": 4,
    "voltage": Voltage.V110,
    "status": DispenserStatus.ACTIVE,
    "notes": "notes",
    "company_id": "com_123",
    "reservation_id": "res_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class BeerDispenserResponse(Response):
    data: BeerDispenserInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Beer dispenser processed with success",
                "data": EXAMPLE_DISPENSER,
            }
        }
    )


class BeerDispenserListResponse(Response):
    data: List[BeerDispenserInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Beer dispensers found with success",
                "data": [EXAMPLE_DISPENSER],
            }
        }
    )
