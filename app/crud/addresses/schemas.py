from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class Address(GenericModel):
    postal_code: str = Field(example="12345-000")
    street: str = Field(example="Main St")
    number: str = Field(example="100")
    complement: str | None = Field(default=None, example="Apt 1")
    district: str = Field(example="Downtown")
    city: str = Field(example="Metropolis")
    state: str = Field(example="SP")
    reference: str | None = Field(default=None, example="Near park")


class AddressInDB(DatabaseModel):
    postal_code: str = Field(example="12345-000")
    street: str = Field(example="Main St")
    number: str = Field(example="100")
    complement: str | None = Field(default=None, example="Apt 1")
    district: str = Field(example="Downtown")
    city: str = Field(example="Metropolis")
    state: str = Field(example="SP")
    reference: str | None = Field(default=None, example="Near park")
    company_id: str = Field(example="com_123")


class UpdateAddress(GenericModel):
    postal_code: str | None = Field(default=None)
    street: str | None = Field(default=None)
    number: str | None = Field(default=None)
    complement: str | None = Field(default=None)
    district: str | None = Field(default=None)
    city: str | None = Field(default=None)
    state: str | None = Field(default=None)
    reference: str | None = Field(default=None)
