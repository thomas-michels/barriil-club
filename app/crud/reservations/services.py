from typing import List
from decimal import Decimal
from datetime import date

from app.core.exceptions import NotFoundError
from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.schemas import KegStatus
from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.crud.pressure_gauges.schemas import PressureGaugeStatus

from .repositories import ReservationRepository
from .schemas import (
    Reservation,
    ReservationInDB,
    UpdateReservation,
    ReservationStatus,
)


class ReservationServices:
    def __init__(
        self,
        reservation_repository: ReservationRepository,
        keg_repository: KegRepository,
        pressure_gauge_repository: PressureGaugeRepository,
    ) -> None:
        self.__repository = reservation_repository
        self.__keg_repository = keg_repository
        self.__pg_repository = pressure_gauge_repository

    async def create(self, reservation: Reservation) -> ReservationInDB:
        total = Decimal("0")
        for keg_id in reservation.keg_ids:
            keg = await self.__keg_repository.select_by_id(
                keg_id, reservation.company_id
            )
            if keg.status in [KegStatus.EMPTY, KegStatus.IN_USE]:
                raise NotFoundError(message=f"Keg #{keg_id} not available")
            price = keg.sale_price_per_l or Decimal("0")
            total += price * Decimal(keg.size_l)

        if reservation.beer_dispenser_id:
            conflict = await self.__repository.find_beer_dispenser_conflict(
                company_id=reservation.company_id,
                beer_dispenser_id=reservation.beer_dispenser_id,
                delivery_date=reservation.delivery_date,
                pickup_date=reservation.pickup_date,
            )
            if conflict:
                raise NotFoundError(
                    message="Beer dispenser already reserved for this period"
                )

        status = reservation.status or self._compute_status(reservation.delivery_date)
        data = reservation.model_dump()
        data["total_value"] = round(total, 2)
        data["status"] = status
        res = await self.__repository.create(reservation=Reservation(**data))
        for keg_id in reservation.keg_ids:
            await self.__keg_repository.update(
                keg_id, reservation.company_id, {"status": KegStatus.IN_USE.value}
            )
        return res

    async def update(
        self, id: str, company_id: str, reservation: UpdateReservation
    ) -> ReservationInDB:
        data = reservation.model_dump(exclude_unset=True, exclude_none=True)
        updated = await self.__repository.update(
            id=id, company_id=company_id, reservation=data
        )
        if updated.status == ReservationStatus.COMPLETED:
            for keg_id in updated.keg_ids:
                await self.__keg_repository.update(
                    keg_id, company_id, {"status": KegStatus.EMPTY.value}
                )
            for pg_id in updated.pressure_gauge_ids:
                await self.__pg_repository.update(
                    pg_id, company_id, {"status": PressureGaugeStatus.TO_VERIFY.value}
                )
        return updated

    async def search_by_id(self, id: str, company_id: str) -> ReservationInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    def _compute_status(self, delivery_date: date) -> ReservationStatus:
        today = date.today()
        if today < delivery_date:
            return ReservationStatus.RESERVED
        if today == delivery_date:
            return ReservationStatus.TO_DELIVER
        return ReservationStatus.DELIVERED

    async def search_all(
        self,
        company_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        status: ReservationStatus | None = None,
    ) -> List[ReservationInDB]:
        status_value = status.value if status else None
        return await self.__repository.select_all(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            status=status_value,
        )

    async def delete_by_id(self, id: str, company_id: str) -> ReservationInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
