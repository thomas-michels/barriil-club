from decimal import Decimal
from datetime import date
from enum import Enum
from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class KegStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    EMPTY = "EMPTY"


class Keg(GenericModel):
    number: str = Field(example="1")
    size_l: int = Field(example=50)
    beer_type_id: str = Field(example="bty_123")
    cost_price_per_l: Decimal = Field(example=5.5)
    sale_price_per_l: Decimal | None = Field(default=None, example=8.0)
    lot: str | None = Field(default=None, example="L001")
    expiration_date: date | None = Field(default=None, example="2025-01-01")
    current_volume_l: Decimal | None = Field(default=None, example=25)
    status: KegStatus = Field(example=KegStatus.AVAILABLE)
    notes: str | None = Field(default=None, example="notes")
    company_id: str = Field(example="com_123")


class KegInDB(DatabaseModel):
    number: str = Field(example="1")
    size_l: int = Field(example=50)
    beer_type_id: str = Field(example="bty_123")
    cost_price_per_l: Decimal = Field(example=5.5)
    sale_price_per_l: Decimal | None = Field(default=None, example=8.0)
    lot: str | None = Field(default=None, example="L001")
    expiration_date: date | None = Field(default=None, example="2025-01-01")
    current_volume_l: Decimal | None = Field(default=None, example=25)
    status: KegStatus = Field(example=KegStatus.AVAILABLE)
    notes: str | None = Field(default=None, example="notes")
    company_id: str = Field(example="com_123")


class UpdateKeg(GenericModel):
    number: str | None = Field(default=None)
    size_l: int | None = Field(default=None)
    beer_type_id: str | None = Field(default=None)
    cost_price_per_l: Decimal | None = Field(default=None)
    sale_price_per_l: Decimal | None = Field(default=None)
    lot: str | None = Field(default=None)
    expiration_date: date | None = Field(default=None)
    current_volume_l: Decimal | None = Field(default=None)
    status: KegStatus | None = Field(default=None)
    notes: str | None = Field(default=None)
