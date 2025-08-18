from typing import List

from pydantic import Field, EmailStr, field_validator

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class Customer(GenericModel):
    name: str = Field(example="John Doe")
    document: str = Field(example="12345678909")
    email: EmailStr | None = Field(default=None, example="john@example.com")
    mobile: str | None = Field(default=None, example="11999999999")
    birth_date: str | None = Field(default=None, example="1990-01-01")
    address_ids: List[str] | None = Field(
        default=None, example=["add_12345678", "add_87654321"]
    )
    notes: str | None = Field(default=None, example="VIP")

    @field_validator("document")
    @classmethod
    def validate_document(cls, v: str) -> str:
        from app.core.utils.validate_document import validate_cpf, validate_cnpj

        if not (validate_cpf(v) or validate_cnpj(v)):
            raise ValueError("Invalid document")
        return v


class CustomerInDB(DatabaseModel):
    name: str = Field(example="John Doe")
    document: str = Field(example="12345678909")
    email: EmailStr | None = Field(default=None, example="john@example.com")
    mobile: str | None = Field(default=None, example="11999999999")
    birth_date: str | None = Field(default=None, example="1990-01-01")
    address_ids: List[str] | None = Field(
        default=None, example=["add_12345678", "add_87654321"]
    )
    notes: str | None = Field(default=None, example="VIP")
    company_id: str = Field(example="com_123")


class UpdateCustomer(GenericModel):
    name: str | None = Field(default=None)
    document: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    mobile: str | None = Field(default=None)
    birth_date: str | None = Field(default=None)
    address_ids: List[str] | None = Field(default=None)
    notes: str | None = Field(default=None)

    @field_validator("document")
    @classmethod
    def validate_document(cls, v: str) -> str:
        from app.core.utils.validate_document import validate_cpf, validate_cnpj

        if v is not None and not (validate_cpf(v) or validate_cnpj(v)):
            raise ValueError("Invalid document")
        return v
