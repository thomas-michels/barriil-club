from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field

from app.crud.reservations.schemas import ReservationInDB


class MonthlyRevenue(BaseModel):
    month: int = Field(ge=1, le=12)
    revenue: Decimal = Field(default=0)
    reservation_count: int = Field(default=0)
    liters_sold: int = Field(default=0)
    cost: Decimal = Field(default=0)
    profit: Decimal = Field(default=0)


class ReservationCalendarDay(BaseModel):
    day: int = Field(ge=1, le=31)
    reservations: List[ReservationInDB] = Field(default_factory=list)
