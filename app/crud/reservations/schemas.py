from decimal import Decimal
from enum import Enum
from typing import List
from decimal import Decimal
from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel
from app.core.utils.utc_datetime import UTCDateTime, UTCDateTimeType
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
    beer_dispenser_ids: List[str] = Field(..., min_length=1, example=["bsd_123"])
    keg_ids: List[str] = Field(..., min_length=1, example=["keg_1"])
    extractor_ids: List[str] = Field(..., min_length=1, example=["ext_1"])
    pressure_gauge_ids: List[str] = Field(..., min_length=1, example=["prg_1"])
    cylinder_ids: List[str] = Field(..., min_length=1, example=["cyl_1"])
    freight_value: Decimal = Field(default=0, example=10.0)
    additional_value: Decimal = Field(default=0, example=0.0)
    discount: Decimal = Field(default=0, example=0.0)
    delivery_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    pickup_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    payments: List[Payment] = Field(default_factory=list)
    total_value: Decimal | None = Field(default=None, example=200.0)
    status: ReservationStatus | None = Field(default=None, example=ReservationStatus.RESERVED)
    company_id: str = Field(example="com_123")


class ReservationInDB(DatabaseModel):
    customer_id: str = Field(example="cus_123")
    address_id: str = Field(example="add_123")
    beer_dispenser_ids: List[str] = Field(..., min_length=1, example=["bsd_123"])
    keg_ids: List[str] = Field(..., min_length=1, example=["keg_1"])
    extractor_ids: List[str] = Field(..., min_length=1, example=["ext_1"])
    pressure_gauge_ids: List[str] = Field(..., min_length=1, example=["prg_1"])
    cylinder_ids: List[str] = Field(..., min_length=1, example=["cyl_1"])
    freight_value: Decimal = Field(example=10.0)
    additional_value: Decimal = Field(example=0.0)
    discount: Decimal = Field(example=0.0)
    delivery_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    pickup_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    payments: List[Payment] = Field(default_factory=list)
    total_value: Decimal = Field(example=200.0)
    status: ReservationStatus = Field(example=ReservationStatus.RESERVED)
    company_id: str = Field(example="com_123")


class UpdateReservation(GenericModel):
    beer_dispenser_ids: List[str] | None = Field(default=None)
    keg_ids: List[str] | None = Field(default=None)
    extractor_ids: List[str] | None = Field(default=None)
    pressure_gauge_ids: List[str] | None = Field(default=None)
    cylinder_ids: List[str] | None = Field(default=None)
    freight_value: Decimal | None = Field(default=None)
    additional_value: Decimal | None = Field(default=None)
    discount: Decimal | None = Field(default=None)
    delivery_date: UTCDateTimeType | None = Field(default=None)
    pickup_date: UTCDateTimeType | None = Field(default=None)
    payments: List[Payment] | None = Field(default=None)
    status: ReservationStatus | None = Field(default=None)
    total_value: Decimal | None = Field(default=None)
