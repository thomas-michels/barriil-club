from pydantic import Field, EmailStr

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel
from app.core.utils.utc_datetime import UTCDateTime, UTCDateTimeType


class CompanyMember(GenericModel):
    user_id: str = Field(example="usr_12345678")
    role: str = Field(example="owner")


class Company(GenericModel):
    name: str = Field(example="ACME")
    address_id: str | None = Field(default=None, example="add_12345678")
    phone_number: str = Field(example="9999-9999")
    ddd: str = Field(example="11")
    email: EmailStr = Field(example="info@acme.com")
    members: list[CompanyMember] = Field(default_factory=list)


class CompanySubscription(GenericModel):
    is_active: bool = Field(example=True)
    expires_at: UTCDateTimeType = Field(example=str(UTCDateTime.now()))


class CompanyInDB(DatabaseModel):
    name: str = Field(example="ACME")
    address_id: str | None = Field(default=None, example="add_12345678")
    phone_number: str = Field(example="9999-9999")
    ddd: str = Field(example="11")
    email: EmailStr = Field(example="info@acme.com")
    members: list[CompanyMember] = Field(default_factory=list)
    subscription: CompanySubscription = Field()


class UpdateCompany(GenericModel):
    name: str | None = Field(default=None)
    address_id: str | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    ddd: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)


class UpdateCompanySubscription(GenericModel):
    is_active: bool | None = Field(default=None, example=True)
    expires_at: UTCDateTimeType | None = Field(default=None)

