from pydantic import Field, EmailStr

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class CompanyMember(GenericModel):
    user_id: str = Field(example="usr_12345678")
    role: str = Field(example="owner")


class Company(GenericModel):
    name: str = Field(example="ACME")
    address_line1: str = Field(example="Street 1")
    address_line2: str | None = Field(default=None, example="Apt 2")
    phone_number: str = Field(example="9999-9999")
    ddd: str = Field(example="11")
    email: EmailStr = Field(example="info@acme.com")
    members: list[CompanyMember] = Field(default_factory=list)


class CompanyInDB(DatabaseModel):
    name: str = Field(example="ACME")
    address_line1: str = Field(example="Street 1")
    address_line2: str | None = Field(default=None, example="Apt 2")
    phone_number: str = Field(example="9999-9999")
    ddd: str = Field(example="11")
    email: EmailStr = Field(example="info@acme.com")
    members: list[CompanyMember] = Field(default_factory=list)


class UpdateCompany(GenericModel):
    name: str | None = Field(default=None)
    address_line1: str | None = Field(default=None)
    address_line2: str | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    ddd: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
