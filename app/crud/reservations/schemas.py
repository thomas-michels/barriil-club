from decimal import Decimal
from enum import Enum
from typing import List

from pydantic import Field, model_validator

from app.core.models.base_model import DatabaseModel
from app.core.models.base_schema import GenericModel
from app.core.utils.utc_datetime import UTCDateTime, UTCDateTimeType
from app.crud.payments.schemas import Payment


class ReservationStatus(str, Enum):
    RESERVED = "RESERVED"
    TO_DELIVER = "TO_DELIVER"
    DELIVERED = "DELIVERED"
    TO_PICKUP = "TO_PICKUP"
    COMPLETED = "COMPLETED"


class Reservation(GenericModel):
    """Input schema for reservation endpoints.

    The original code required both ``extractor_ids`` and
    ``extraction_kit_ids`` to be provided which did not match the payload
    used in the tests.  The tests send only ``extractorIds`` (old naming) and
    an additional ``ExtractionKitIds`` field which should be ignored.  To
    handle this we make ``extraction_kit_ids`` optional and, if omitted,
    populate it with the value of ``extractor_ids``.

    We also allow extra fields to be ignored so that legacy clients sending
    ``ExtractionKitIds`` do not trigger validation errors.
    """

    model_config = GenericModel.model_config.copy()
    model_config["extra"] = "ignore"

    customer_id: str = Field(example="cus_123")
    address_id: str = Field(example="add_123")
    beer_dispenser_ids: List[str] = Field(..., min_length=1, example=["bsd_123"])
    keg_ids: List[str] = Field(..., min_length=1, example=["keg_1"])
    extractor_ids: List[str] | None = Field(
        default=None, alias="extractorIds"
    )
    extraction_kit_ids: List[str] | None = Field(
        default=None, alias="extractionKitIds"
    )
    cylinder_ids: List[str] = Field(..., min_length=1, example=["cyl_1"])
    freight_value: Decimal = Field(default=0, example=10.0)
    additional_value: Decimal = Field(default=0, example=0.0)
    discount: Decimal = Field(default=0, example=0.0)
    delivery_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    pickup_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    payments: List[Payment] = Field(default_factory=list)

    @model_validator(mode="before")
    def _forbid_status(cls, data):
        if isinstance(data, dict) and data.get("status") is not None:
            raise ValueError("status field is not allowed")
        return data

    @model_validator(mode="after")
    def _sync_extraction_kit_ids(self) -> "Reservation":
        if not self.extractor_ids and not self.extraction_kit_ids:
            raise ValueError("At least one extraction kit is required")
        if not self.extraction_kit_ids:
            self.extraction_kit_ids = list(self.extractor_ids)
        if not self.extractor_ids:
            self.extractor_ids = list(self.extraction_kit_ids)
        return self


class ReservationCreate(GenericModel):
    customer_id: str = Field(example="cus_123")
    address_id: str = Field(example="add_123")
    beer_dispenser_ids: List[str] = Field(..., min_length=1, example=["bsd_123"])
    keg_ids: List[str] = Field(..., min_length=1, example=["keg_1"])
    extraction_kit_ids: List[str] = Field(
        ..., min_length=1, example=["prg_1"]
    )
    extractor_ids: List[str] | None = Field(
        default=None, alias="extractorIds"
    )
    cylinder_ids: List[str] = Field(..., min_length=1, example=["cyl_1"])
    freight_value: Decimal = Field(example=10.0)
    additional_value: Decimal = Field(example=0.0)
    discount: Decimal = Field(example=0.0)
    delivery_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    pickup_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    payments: List[Payment] = Field(default_factory=list)
    total_value: Decimal = Field(example=200.0)
    total_cost: Decimal = Field(example=150.0)
    status: ReservationStatus = Field(example=ReservationStatus.RESERVED)

    @model_validator(mode="after")
    def _sync_extractor_ids(self) -> "ReservationCreate":
        if self.extractor_ids is None:
            self.extractor_ids = list(self.extraction_kit_ids)
        return self


class ReservationInDB(DatabaseModel):
    customer_id: str = Field(example="cus_123")
    address_id: str = Field(example="add_123")
    beer_dispenser_ids: List[str] = Field(..., min_length=1, example=["bsd_123"])
    keg_ids: List[str] = Field(..., min_length=1, example=["keg_1"])
    extractor_ids: List[str] = Field(..., min_length=1, example=["ext_1"])
    extraction_kit_ids: List[str] = Field(..., min_length=1, example=["prg_1"])
    cylinder_ids: List[str] = Field(..., min_length=1, example=["cyl_1"])
    freight_value: Decimal = Field(example=10.0)
    additional_value: Decimal = Field(example=0.0)
    discount: Decimal = Field(example=0.0)
    delivery_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    pickup_date: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    payments: List[Payment] = Field(default_factory=list)
    total_value: Decimal = Field(example=200.0)
    total_cost: Decimal = Field(default=0, example=150.0)
    status: ReservationStatus = Field(example=ReservationStatus.RESERVED)
    company_id: str = Field(example="com_123")


class UpdateReservation(GenericModel):
    beer_dispenser_ids: List[str] | None = Field(default=None)
    keg_ids: List[str] | None = Field(default=None)
    extractor_ids: List[str] | None = Field(default=None)
    extraction_kit_ids: List[str] | None = Field(default=None)
    cylinder_ids: List[str] | None = Field(default=None)
    freight_value: Decimal | None = Field(default=None)
    additional_value: Decimal | None = Field(default=None)
    discount: Decimal | None = Field(default=None)
    delivery_date: UTCDateTimeType | None = Field(default=None)
    pickup_date: UTCDateTimeType | None = Field(default=None)
    payments: List[Payment] | None = Field(default=None)
    status: ReservationStatus | None = Field(default=None)
    total_value: Decimal | None = Field(default=None)
    total_cost: Decimal | None = Field(default=None)
