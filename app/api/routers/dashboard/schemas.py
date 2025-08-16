from typing import List
from pydantic import Field, ConfigDict

from app.api.shared_schemas.responses import Response
from app.crud.dashboard.schemas import MonthlyRevenue, ReservationCalendarDay


class MonthlyRevenueResponse(Response):
    data: List[MonthlyRevenue] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Monthly revenue found with success",
                "data": [
                    {
                        "month": 1,
                        "revenue": 100.0,
                        "reservation_count": 1,
                        "liters_sold": 50,
                        "cost": 50.0,
                        "profit": 50.0,
                    }
                ],
            }
        }
    )


class ReservationCalendarResponse(Response):
    data: List[ReservationCalendarDay] = Field()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Reservation calendar found with success",
                "data": [
                    {
                        "day": 1,
                        "reservations": [],
                    }
                ],
            }
        }
    )
