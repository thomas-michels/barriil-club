from decimal import Decimal
from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class BeerType(GenericModel):
    name: str = Field(example="Pale Ale")
    producer: str | None = Field(default=None, example="Brew Co")
    abv: Decimal | None = Field(default=None, example=5.0)
    ibu: Decimal | None = Field(default=None, example=40.0)
    description: str | None = Field(default=None, example="Tasty beer")
    default_sale_price_per_l: Decimal = Field(example=10.5)


class BeerTypeInDB(DatabaseModel):
    name: str = Field(example="Pale Ale")
    producer: str | None = Field(default=None, example="Brew Co")
    abv: Decimal | None = Field(default=None, example=5.0)
    ibu: Decimal | None = Field(default=None, example=40.0)
    description: str | None = Field(default=None, example="Tasty beer")
    default_sale_price_per_l: Decimal = Field(example=10.5)
    company_id: str = Field(example="com_123")


class UpdateBeerType(GenericModel):
    name: str | None = Field(default=None)
    producer: str | None = Field(default=None)
    abv: Decimal | None = Field(default=None)
    ibu: Decimal | None = Field(default=None)
    description: str | None = Field(default=None)
    default_sale_price_per_l: Decimal | None = Field(default=None)
