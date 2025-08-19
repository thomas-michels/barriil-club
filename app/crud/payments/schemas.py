from decimal import Decimal
from enum import Enum
from datetime import date

from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.crud.customers.schemas import CustomerInDB


class Payment(GenericModel):
    amount: Decimal = Field(example=100.0)
    method: str = Field(example="CASH")
    paid_at: date = Field(example=str(date.today()))


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class PaymentWithCustomer(GenericModel):
    reservation_id: str = Field(example="res_123")
    customer: CustomerInDB = Field()
    total_value: Decimal = Field(example=100.0)
    paid_value: Decimal = Field(example=50.0)
    pending_value: Decimal = Field(example=50.0)
    status: PaymentStatus = Field(example=PaymentStatus.PENDING)
