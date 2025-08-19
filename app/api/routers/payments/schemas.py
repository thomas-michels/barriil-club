from typing import List

from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.payments.schemas import PaymentWithCustomer, PaymentStatus

EXAMPLE_PAYMENT = {
    "reservation_id": "res_123",
    "customer": {
        "id": "cus_123",
        "name": "John Doe",
        "document": "10000000019",
        "email": "john@example.com",
        "mobile": "11999999999",
        "birth_date": "1990-01-01",
        "addressIds": [],
        "notes": "",
        "company_id": "com_1",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    },
    "total_value": 100.0,
    "paid_value": 100.0,
    "pending_value": 0.0,
    "status": PaymentStatus.PAID,
}


class PaymentListResponse(Response):
    data: List[PaymentWithCustomer] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Payments found with success",
                "data": [EXAMPLE_PAYMENT],
            }
        }
    )
