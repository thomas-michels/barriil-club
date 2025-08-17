from typing import List

from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.companies.schemas import (
    CompanyInDB,
    CompanyMember,
    CompanySubscription,
)

EXAMPLE_COMPANY = {
    "id": "com_12345678",
    "name": "ACME",
    "addressId": "add_12345678",
    "phone_number": "9999-9999",
    "ddd": "11",
    "email": "info@acme.com",
    "members": [{"user_id": "usr_1", "role": "owner"}],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "subscription": {"is_active": True, "expires_at": "2024-01-08T00:00:00Z"},
}

EXAMPLE_SUBSCRIPTION = {
    "is_active": True,
    "expires_at": "2024-01-08T00:00:00Z",
}


class CompanyResponse(Response):
    data: CompanyInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Company processed with success", "data": EXAMPLE_COMPANY}
        }
    )


class CompanyListResponse(Response):
    data: List[CompanyInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Companies found with success",
                "data": [EXAMPLE_COMPANY],
            }
        }
    )


class SubscriptionResponse(Response):
    data: CompanySubscription | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Subscription processed with success",
                "data": EXAMPLE_SUBSCRIPTION,
            }
        }
    )
