from __future__ import annotations

from datetime import timedelta
import calendar
from decimal import Decimal
from typing import List

from app.core.utils.utc_datetime import UTCDateTime
from app.crud.reservations.services import ReservationServices
from app.crud.reservations.schemas import ReservationInDB
from app.crud.kegs.services import KegServices
from .schemas import MonthlyRevenue, ReservationCalendarDay


class DashboardServices:
    def __init__(
        self,
        reservation_services: ReservationServices,
        keg_services: KegServices,
    ) -> None:
        self.__reservation_services = reservation_services
        self.__keg_services = keg_services

    async def monthly_revenue(self, company_id: str, year: int) -> List[MonthlyRevenue]:
        start = UTCDateTime(year, 1, 1)
        end = UTCDateTime(year, 12, 31, 23, 59, 59)
        reservations = await self.__reservation_services.search_all(
            company_id=company_id, start_date=start, end_date=end
        )
        monthly = {
            i: {
                "revenue": Decimal("0"),
                "count": 0,
                "liters": 0,
                "cost": Decimal("0"),
            }
            for i in range(1, 13)
        }
        for res in reservations:
            month = res.delivery_date.month
            stats = monthly[month]
            stats["revenue"] += res.total_value
            stats["count"] += 1
            for keg_id in res.keg_ids:
                keg = await self.__keg_services.search_by_id(keg_id, company_id)
                stats["liters"] += keg.size_l
                stats["cost"] += keg.cost_price_per_l * Decimal(keg.size_l)
        result: List[MonthlyRevenue] = []
        for m, v in monthly.items():
            profit = v["revenue"] - v["cost"]
            result.append(
                MonthlyRevenue(
                    month=m,
                    revenue=v["revenue"],
                    reservation_count=v["count"],
                    liters_sold=v["liters"],
                    cost=v["cost"],
                    profit=profit,
                )
            )
        return result

    async def upcoming_reservations(self, company_id: str) -> List[ReservationInDB]:
        start = UTCDateTime.now()
        end = start + timedelta(days=7)
        return await self.__reservation_services.search_all(
            company_id=company_id, start_date=start, end_date=end
        )

    async def reservation_calendar(
        self, company_id: str, year: int, month: int
    ) -> List[ReservationCalendarDay]:
        start = UTCDateTime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end = UTCDateTime(year, month, last_day, 23, 59, 59)
        reservations = await self.__reservation_services.search_all(
            company_id=company_id, start_date=start, end_date=end
        )
        days = {day: [] for day in range(1, last_day + 1)}
        for res in reservations:
            day = res.delivery_date.day
            days[day].append(res)
        return [
            ReservationCalendarDay(day=day, reservations=items)
            for day, items in days.items()
        ]
