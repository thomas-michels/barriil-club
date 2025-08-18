from typing import List

from .repositories import KegRepository
from .schemas import Keg, KegInDB, UpdateKeg


class KegServices:
    def __init__(self, keg_repository: KegRepository) -> None:
        self.__repository = keg_repository

    async def create(self, keg: Keg, company_id: str) -> KegInDB:
        return await self.__repository.create(keg=keg, company_id=company_id)

    async def update(self, id: str, company_id: str, keg: UpdateKeg) -> KegInDB:
        data = keg.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(keg_id=id, company_id=company_id, keg=data)

    async def search_by_id(self, id: str, company_id: str) -> KegInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    async def search_all(self, company_id: str) -> List[KegInDB]:
        return await self.__repository.select_all(company_id=company_id)

    async def delete_by_id(self, id: str, company_id: str) -> KegInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
