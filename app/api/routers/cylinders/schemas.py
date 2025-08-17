from typing import List
from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.cylinders.schemas import CylinderInDB, CylinderStatus

EXAMPLE_CYLINDER = {
    "id": "cyl_12345678",
    "brand": "Acme",
    "weight_kg": 10.5,
    "number": "CY123",
    "status": CylinderStatus.AVAILABLE,
    "notes": "notes",
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class CylinderResponse(Response):
    data: CylinderInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Cylinder processed with success",
                "data": EXAMPLE_CYLINDER,
            }
        }
    )


class CylinderListResponse(Response):
    data: List[CylinderInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Cylinders found with success",
                "data": [EXAMPLE_CYLINDER],
            }
        }
    )
