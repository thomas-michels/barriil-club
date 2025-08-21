from typing import List
from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.reservations.schemas import ReservationInDB, ReservationStatus

EXAMPLE_RESERVATION = {
    "id": "res_12345678",
    "customer_id": "cus_123",
    "address_id": "add_123",
    "beer_dispenser_ids": ["bsd_123"],
    "keg_ids": ["keg_1"],
    "extractor_ids": ["ext_1"],
    "pressure_gauge_ids": ["prg_1"],
    "cylinder_ids": ["cyl_1"],
    "freight_value": 10.0,
    "additional_value": 0.0,
    "discount": 0.0,
    "delivery_date": "2024-01-01T10:00:00Z",
    "pickup_date": "2024-01-02T10:00:00Z",
    "payments": [],
    "total_value": 200.0,
    "total_cost": 150.0,
    "status": ReservationStatus.RESERVED,
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class ReservationResponse(Response):
    data: ReservationInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Reservation processed with success",
                "data": EXAMPLE_RESERVATION,
            }
        }
    )


class ReservationListResponse(Response):
    data: List[ReservationInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Reservations found with success",
                "data": [EXAMPLE_RESERVATION],
            }
        }
    )
