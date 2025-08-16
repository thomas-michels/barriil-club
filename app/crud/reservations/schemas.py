from decimal import Decimal
from datetime import date
from enum import Enum
from typing import List
from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel
from app.crud.payments.schemas import Payment


class ReservationStatus(str, Enum):
    RESERVED = "RESERVED"
    TO_DELIVER = "TO_DELIVER"
    DELIVERED = "DELIVERED"
    TO_PICKUP = "TO_PICKUP"
    COMPLETED = "COMPLETED"
class Reservation(GenericModel):
    customer_id: str = Field(example="cus_123")
    address_id: str = Field(example="add_123")
    beer_dispenser_id: str | None = Field(default=None, example="bsd_123")
    keg_ids: List[str] = Field(default_factory=list, example=["keg_1"])
    extractor_ids: List[str] = Field(default_factory=list, example=["ext_1"])
    pressure_gauge_ids: List[str] = Field(default_factory=list, example=["prg_1"])
    delivery_date: date = Field(example=str(date.today()))
    pickup_date: date = Field(example=str(date.today()))
    payments: List[Payment] = Field(default_factory=list)
    total_value: Decimal | None = Field(default=None, example=200.0)
    status: ReservationStatus | None = Field(default=None, example=ReservationStatus.RESERVED)
    company_id: str = Field(example="com_123")


class ReservationInDB(DatabaseModel):
    customer_id: str = Field(example="cus_123")
    address_id: str = Field(example="add_123")
    beer_dispenser_id: str | None = Field(default=None, example="bsd_123")
    keg_ids: List[str] = Field(default_factory=list, example=["keg_1"])
    extractor_ids: List[str] = Field(default_factory=list, example=["ext_1"])
    pressure_gauge_ids: List[str] = Field(default_factory=list, example=["prg_1"])
    delivery_date: date = Field(example=str(date.today()))
    pickup_date: date = Field(example=str(date.today()))
    payments: List[Payment] = Field(default_factory=list)
    total_value: Decimal = Field(example=200.0)
    status: ReservationStatus = Field(example=ReservationStatus.RESERVED)
    company_id: str = Field(example="com_123")


class UpdateReservation(GenericModel):
    beer_dispenser_id: str | None = Field(default=None)
    keg_ids: List[str] | None = Field(default=None)
    extractor_ids: List[str] | None = Field(default=None)
    pressure_gauge_ids: List[str] | None = Field(default=None)
    delivery_date: date | None = Field(default=None)
    pickup_date: date | None = Field(default=None)
    payments: List[Payment] | None = Field(default=None)
    status: ReservationStatus | None = Field(default=None)
    total_value: Decimal | None = Field(default=None)
