from typing import List

from .repositories import ExtractionKitRepository
from .schemas import ExtractionKit, ExtractionKitInDB, UpdateExtractionKit


class ExtractionKitServices:
    def __init__(self, repository: ExtractionKitRepository) -> None:
        self.__repository = repository

    async def create(self, gauge: ExtractionKit, company_id: str) -> ExtractionKitInDB:
        return await self.__repository.create(gauge=gauge, company_id=company_id)

    async def update(
        self, id: str, company_id: str, gauge: UpdateExtractionKit
    ) -> ExtractionKitInDB:
        data = gauge.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(
            gauge_id=id, company_id=company_id, gauge=data
        )

    async def search_by_id(self, id: str, company_id: str) -> ExtractionKitInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    async def search_all(self, company_id: str) -> List[ExtractionKitInDB]:
        return await self.__repository.select_all(company_id=company_id)

    async def delete_by_id(self, id: str, company_id: str) -> ExtractionKitInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
