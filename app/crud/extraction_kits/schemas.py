from datetime import date
from enum import Enum

from pydantic import Field

from app.core.models.base_model import DatabaseModel
from app.core.models.base_schema import GenericModel


class ExtractionKitType(str, Enum):
    SIMPLE = "SIMPLE"
    DOUBLE = "DOUBLE"


class ExtractionKitStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    TO_VERIFY = "TO_VERIFY"


class ExtractionKit(GenericModel):
    type: ExtractionKitType = Field(example=ExtractionKitType.SIMPLE)
    last_calibration_date: date | None = Field(default=None, example="2024-01-01")
    status: ExtractionKitStatus = Field(example=ExtractionKitStatus.ACTIVE)
    notes: str | None = Field(default=None, example="notes")


class ExtractionKitInDB(DatabaseModel):
    type: ExtractionKitType = Field(example=ExtractionKitType.SIMPLE)
    last_calibration_date: date | None = Field(default=None, example="2024-01-01")
    status: ExtractionKitStatus = Field(example=ExtractionKitStatus.ACTIVE)
    notes: str | None = Field(default=None, example="notes")
    company_id: str = Field(example="com_123")


class UpdateExtractionKit(GenericModel):
    type: ExtractionKitType | None = Field(default=None)
    last_calibration_date: date | None = Field(default=None)
    status: ExtractionKitStatus | None = Field(default=None)
    notes: str | None = Field(default=None)
