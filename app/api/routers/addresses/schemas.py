from typing import List

from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.addresses.schemas import Address, AddressInDB

EXAMPLE_ADDRESS = {
    "id": "add_12345678",
    "postal_code": "12345-000",
    "street": "Main St",
    "number": "100",
    "complement": "Apt 1",
    "district": "Downtown",
    "city": "Metropolis",
    "state": "SP",
    "reference": "Near park",
    "company_id": "com_123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class AddressResponse(Response):
    data: Address | AddressInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Address processed with success", "data": EXAMPLE_ADDRESS}
        }
    )


class AddressListResponse(Response):
    data: List[AddressInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Addresses found with success",
                "data": [EXAMPLE_ADDRESS],
            }
        }
    )
