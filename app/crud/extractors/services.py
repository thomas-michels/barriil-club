from typing import List

from .repositories import ExtractorRepository
from .schemas import Extractor, ExtractorInDB, UpdateExtractor


class ExtractorServices:
    def __init__(self, extractor_repository: ExtractorRepository) -> None:
        self.__repository = extractor_repository

    async def create(self, extractor: Extractor, company_id: str) -> ExtractorInDB:
        return await self.__repository.create(extractor=extractor, company_id=company_id)

    async def update(
        self, id: str, company_id: str, extractor: UpdateExtractor
    ) -> ExtractorInDB:
        data = extractor.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(
            extractor_id=id, company_id=company_id, extractor=data
        )

    async def search_by_id(self, id: str, company_id: str) -> ExtractorInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    async def search_all(self, company_id: str) -> List[ExtractorInDB]:
        return await self.__repository.select_all(company_id=company_id)

    async def delete_by_id(self, id: str, company_id: str) -> ExtractorInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
