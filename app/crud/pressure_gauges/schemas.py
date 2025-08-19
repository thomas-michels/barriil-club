from datetime import date
from enum import Enum
from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class PressureGaugeType(str, Enum):
    SIMPLE = "SIMPLE"
    DOUBLE = "DOUBLE"


class PressureGaugeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    TO_VERIFY = "TO_VERIFY"


class PressureGauge(GenericModel):
    brand: str = Field(example="Acme")
    type: PressureGaugeType = Field(example=PressureGaugeType.SIMPLE)
    serial_number: str | None = Field(default=None, example="SN123")
    last_calibration_date: date | None = Field(default=None, example="2024-01-01")
    status: PressureGaugeStatus = Field(example=PressureGaugeStatus.ACTIVE)
    notes: str | None = Field(default=None, example="notes")


class PressureGaugeInDB(DatabaseModel):
    brand: str = Field(example="Acme")
    type: PressureGaugeType = Field(example=PressureGaugeType.SIMPLE)
    serial_number: str | None = Field(default=None, example="SN123")
    last_calibration_date: date | None = Field(default=None, example="2024-01-01")
    status: PressureGaugeStatus = Field(example=PressureGaugeStatus.ACTIVE)
    notes: str | None = Field(default=None, example="notes")
    company_id: str = Field(example="com_123")


class UpdatePressureGauge(GenericModel):
    brand: str | None = Field(default=None)
    type: PressureGaugeType | None = Field(default=None)
    serial_number: str | None = Field(default=None)
    last_calibration_date: date | None = Field(default=None)
    status: PressureGaugeStatus | None = Field(default=None)
    notes: str | None = Field(default=None)
