from typing import List

from .repositories import BeerDispenserRepository
from .schemas import BeerDispenser, BeerDispenserInDB, UpdateBeerDispenser


class BeerDispenserServices:
    def __init__(self, repository: BeerDispenserRepository) -> None:
        self.__repository = repository

    async def create(self, dispenser: BeerDispenser, company_id: str) -> BeerDispenserInDB:
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
        return await self.__repository.select_all(company_id=company_id)

    async def delete_by_id(self, id: str, company_id: str) -> BeerDispenserInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
