from typing import List

from .repositories import BeerDispenserRepository
from .schemas import BeerDispenser, BeerDispenserInDB, UpdateBeerDispenser
from .models import BeerDispenserModel
from app.crud.reservations.repositories import ReservationRepository


class BeerDispenserServices:
    def __init__(
        self,
        repository: BeerDispenserRepository,
        reservation_repository: ReservationRepository | None = None,
    ) -> None:
        self.__repository = repository
        self.__reservation_repository = reservation_repository or ReservationRepository()

    async def create(self, dispenser: BeerDispenser, company_id: str) -> BeerDispenserInDB:
        if dispenser.serial_number is not None:
            existing = BeerDispenserModel.objects(
                serial_number__startswith=dispenser.serial_number,
                company_id=company_id,
            ).count()
            if existing > 0:
                dispenser.serial_number = f"{dispenser.serial_number}{existing}"
        return await self.__repository.create(dispenser=dispenser, company_id=company_id)

    async def update(
        self, id: str, company_id: str, dispenser: UpdateBeerDispenser
    ) -> BeerDispenserInDB:
        data = dispenser.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(
            dispenser_id=id, company_id=company_id, dispenser=data
        )

    async def search_by_id(
        self, id: str, company_id: str
    ) -> BeerDispenserInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    async def search_all(self, company_id: str) -> List[BeerDispenserInDB]:
        dispensers = await self.__repository.select_all(company_id=company_id)
        for dispenser in dispensers:
            reservation = await self.__reservation_repository.find_active_by_beer_dispenser_id(
                company_id=company_id, dispenser_id=str(dispenser.id)
            )
            dispenser.reservation_id = reservation.id if reservation else None
        return dispensers

    async def delete_by_id(self, id: str, company_id: str) -> BeerDispenserInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
