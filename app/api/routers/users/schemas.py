from typing import List

from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.users.schemas import UserInDB
from app.crud.companies.schemas import CompanyInDB

EXAMPLE_USER = {
    "user_id": "id-123",
    "email": "test@test.com",
    "name": "Test",
    "nickname": "test",
    "picture": "http://localhost/image.png",
    "user_metadata": {"phone": "123"},
    "app_metadata": {},
    "last_login": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}

EXAMPLE_COMPANY = {
    "id": "cmp-123",
    "name": "ACME",
    "address_id": "add-123",
    "phone_number": "9999-9999",
    "ddd": "11",
    "email": "info@acme.com",
    "members": [],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class CurrentUser(UserInDB):
    company: CompanyInDB | None = Field(default=None)


class GetCurrentUserResponse(Response):
    data: CurrentUser | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "User found with success",
                "data": {**EXAMPLE_USER, "company": EXAMPLE_COMPANY},
            }
        }
    )


class GetUserByIdResponse(Response):
    data: UserInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "User found with success", "data": EXAMPLE_USER}
        }
    )


class GetUsersResponse(Response):
    data: List[UserInDB] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Users found with success",
                "data": [
                    EXAMPLE_USER,
                    {
                        **EXAMPLE_USER,
                        "user_id": "id-456",
                        "email": "second@test.com",
                    },
                ],
            }
        }
    )


class UpdateCurrentUserResponse(Response):
    data: UserInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "User updated with success", "data": EXAMPLE_USER}
        }
    )


class UpdateUserResponse(Response):
    data: UserInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "User updated with success", "data": EXAMPLE_USER}
        }
    )


class DeleteUserResponse(Response):
    data: UserInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "User deleted with success", "data": EXAMPLE_USER}
        }
    )


class DeleteCurrentUserResponse(Response):
    data: UserInDB | None = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "User deleted with success", "data": EXAMPLE_USER}
        }
    )
