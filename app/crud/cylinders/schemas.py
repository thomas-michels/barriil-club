from decimal import Decimal
from enum import Enum
from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class CylinderStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    TO_VERIFY = "TO_VERIFY"


class Cylinder(GenericModel):
    brand: str = Field(example="Acme")
    weight_kg: Decimal = Field(example=10.5)
    number: str = Field(example="CY123")
    status: CylinderStatus = Field(example=CylinderStatus.AVAILABLE)
    notes: str | None = Field(default=None, example="notes")


class CylinderInDB(DatabaseModel):
    brand: str = Field(example="Acme")
    weight_kg: Decimal = Field(example=10.5)
    number: str = Field(example="CY123")
    status: CylinderStatus = Field(example=CylinderStatus.AVAILABLE)
    notes: str | None = Field(default=None, example="notes")
    company_id: str = Field(example="com_123")


class UpdateCylinder(GenericModel):
    brand: str | None = Field(default=None)
    weight_kg: Decimal | None = Field(default=None)
    number: str | None = Field(default=None)
    status: CylinderStatus | None = Field(default=None)
    notes: str | None = Field(default=None)
