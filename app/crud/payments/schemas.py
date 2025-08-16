from decimal import Decimal
from datetime import date
from pydantic import Field

from app.core.models.base_schema import GenericModel


class Payment(GenericModel):
    amount: Decimal = Field(example=100.0)
    method: str = Field(example="CASH")
    paid_at: date = Field(example=str(date.today()))
