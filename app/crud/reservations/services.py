from typing import List
from decimal import Decimal

from app.core.exceptions import BadRequestError
from app.core.utils.utc_datetime import UTCDateTime
from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.schemas import KegStatus
from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.crud.pressure_gauges.schemas import PressureGaugeStatus
from app.crud.cylinders.repositories import CylinderRepository
from app.crud.cylinders.schemas import CylinderStatus
from app.crud.payments.schemas import Payment

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
        cylinder_repository: CylinderRepository,
    ) -> None:
        self.__repository = reservation_repository
        self.__keg_repository = keg_repository
        self.__pg_repository = pressure_gauge_repository
        self.__cylinder_repository = cylinder_repository

    async def create(self, reservation: Reservation, company_id: str) -> ReservationInDB:
        if not reservation.beer_dispenser_ids:
            raise BadRequestError(message="At least one beer dispenser is required")
        if not reservation.keg_ids:
            raise BadRequestError(message="At least one keg is required")
        if not reservation.extractor_ids:
            raise BadRequestError(message="At least one extractor is required")
        if not reservation.pressure_gauge_ids:
            raise BadRequestError(message="At least one pressure gauge is required")
        if not reservation.cylinder_ids:
            raise BadRequestError(message="At least one cylinder is required")

        total = Decimal("0")
        for keg_id in reservation.keg_ids:
            keg = await self.__keg_repository.select_by_id(
                keg_id, company_id
            )
            if keg.status in [KegStatus.EMPTY, KegStatus.IN_USE]:
                raise BadRequestError(message=f"Keg #{keg_id} not available")
            price = keg.sale_price_per_l or Decimal("0")
            total += price * Decimal(keg.size_l)

        for cylinder_id in reservation.cylinder_ids:
            cylinder = await self.__cylinder_repository.select_by_id(
                cylinder_id, company_id
            )
            if cylinder.status != CylinderStatus.AVAILABLE:
                raise BadRequestError(
                    message=f"Cylinder #{cylinder_id} not available"
                )
            if cylinder.weight_kg <= Decimal("0"):
                raise BadRequestError(
                    message=f"Cylinder #{cylinder_id} empty"
                )

        conflict = await self.__repository.find_beer_dispenser_conflict(
            company_id=company_id,
            beer_dispenser_ids=reservation.beer_dispenser_ids,
            delivery_date=reservation.delivery_date,
            pickup_date=reservation.pickup_date,
        )
        if conflict:
            raise BadRequestError(
                message="Beer dispenser already reserved for this period"
            )

        conflict = await self.__repository.find_extractor_conflict(
            company_id=company_id,
            extractor_ids=reservation.extractor_ids,
            delivery_date=reservation.delivery_date,
            pickup_date=reservation.pickup_date,
        )
        if conflict:
            raise BadRequestError(
                message="Extractor already reserved for this period"
            )

        conflict = await self.__repository.find_pressure_gauge_conflict(
            company_id=company_id,
            pressure_gauge_ids=reservation.pressure_gauge_ids,
            delivery_date=reservation.delivery_date,
            pickup_date=reservation.pickup_date,
        )
        if conflict:
            raise BadRequestError(
                message="Pressure gauge already reserved for this period"
            )

        conflict = await self.__repository.find_cylinder_conflict(
            company_id=company_id,
            cylinder_ids=reservation.cylinder_ids,
            delivery_date=reservation.delivery_date,
            pickup_date=reservation.pickup_date,
        )
        if conflict:
            raise BadRequestError(
                message="Cylinder already reserved for this period"
            )

        total += reservation.freight_value
        total += reservation.additional_value
        total -= reservation.discount

        status = reservation.status or self._compute_status(reservation.delivery_date)
        data = reservation.model_dump()
        data["total_value"] = round(total, 2)
        data["status"] = status
        data["company_id"] = company_id
        res = await self.__repository.create(
            reservation=Reservation(**data), company_id=company_id
        )
        for keg_id in reservation.keg_ids:
            await self.__keg_repository.update(
                keg_id, company_id, {"status": KegStatus.IN_USE.value}
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
            for cyl_id in updated.cylinder_ids:
                await self.__cylinder_repository.update(
                    cyl_id, company_id, {"status": CylinderStatus.TO_VERIFY.value}
                )
        return updated

    async def search_by_id(self, id: str, company_id: str) -> ReservationInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    def _compute_status(self, delivery_date: UTCDateTime) -> ReservationStatus:
        now = UTCDateTime.now()
        if now < delivery_date:
            return ReservationStatus.RESERVED
        if now.date() == delivery_date.date():
            return ReservationStatus.TO_DELIVER
        return ReservationStatus.DELIVERED

    async def search_all(
        self,
        company_id: str,
        start_date: UTCDateTime | None = None,
        end_date: UTCDateTime | None = None,
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

    async def add_payment(
        self, id: str, company_id: str, payment: Payment
    ) -> ReservationInDB:
        return await self.__repository.add_payment(
            id=id, company_id=company_id, payment=payment
        )

    async def update_payment(
        self, id: str, company_id: str, index: int, payment: Payment
    ) -> ReservationInDB:
        return await self.__repository.update_payment(
            id=id, company_id=company_id, index=index, payment=payment
        )

    async def delete_payment(
        self, id: str, company_id: str, index: int
    ) -> ReservationInDB:
        return await self.__repository.delete_payment(
            id=id, company_id=company_id, index=index
        )
