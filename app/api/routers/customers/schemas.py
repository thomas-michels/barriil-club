from typing import List

from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.customers.schemas import CustomerInDB

EXAMPLE_CUSTOMER = {
    "id": "cus_12345678",
    "name": "John Doe",
    "document": "12345678909",
    "email": "john@example.com",
    "mobile": "11999999999",
    "birth_date": "1990-01-01",
    "addressIds": ["add_12345678"],
    "notes": "VIP",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class CustomerResponse(Response):
    data: CustomerInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Customer processed with success",
                "data": EXAMPLE_CUSTOMER,
            }
        }
    )


class CustomerListResponse(Response):
    data: List[CustomerInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Customers found with success",
                "data": [EXAMPLE_CUSTOMER],
            }
        }
    )
