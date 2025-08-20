from enum import Enum
from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class Voltage(str, Enum):
    V110 = "110V"
    V220 = "220V"


class DispenserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"


class BeerDispenser(GenericModel):
    brand: str = Field(example="Acme")
    model: str | None = Field(default=None, example="X1")
    serial_number: str | None = Field(default=None, example="SN123")
    taps_count: int | None = Field(default=None, example=4)
    voltage: Voltage | None = Field(default=None, example=Voltage.V110)
    status: DispenserStatus = Field(example=DispenserStatus.ACTIVE)
    notes: str | None = Field(default=None, example="notes")


class BeerDispenserInDB(DatabaseModel):
    brand: str = Field(example="Acme")
    model: str | None = Field(default=None, example="X1")
    serial_number: str | None = Field(default=None, example="SN123")
    taps_count: int | None = Field(default=None, example=4)
    voltage: Voltage | None = Field(default=None, example=Voltage.V110)
    status: DispenserStatus = Field(example=DispenserStatus.ACTIVE)
    notes: str | None = Field(default=None, example="notes")
    company_id: str = Field(example="com_123")
    reservation_id: str | None = Field(default=None, example="res_123")


class UpdateBeerDispenser(GenericModel):
    brand: str | None = Field(default=None)
    model: str | None = Field(default=None)
    serial_number: str | None = Field(default=None)
    taps_count: int | None = Field(default=None)
    voltage: Voltage | None = Field(default=None)
    status: DispenserStatus | None = Field(default=None)
    notes: str | None = Field(default=None)
