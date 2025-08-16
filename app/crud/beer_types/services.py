from typing import List

from .repositories import BeerTypeRepository
from .schemas import BeerType, BeerTypeInDB, UpdateBeerType


class BeerTypeServices:
    def __init__(self, beer_type_repository: BeerTypeRepository) -> None:
        self.__repository = beer_type_repository

    async def create(self, beer_type: BeerType) -> BeerTypeInDB:
        return await self.__repository.create(beer_type=beer_type)

    async def update(
        self, id: str, company_id: str, beer_type: UpdateBeerType
    ) -> BeerTypeInDB:
        data = beer_type.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(
            beer_type_id=id, company_id=company_id, beer_type=data
        )

    async def search_by_id(self, id: str, company_id: str) -> BeerTypeInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    async def search_all(self, company_id: str) -> List[BeerTypeInDB]:
        return await self.__repository.select_all(company_id=company_id)

    async def delete_by_id(self, id: str, company_id: str) -> BeerTypeInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
