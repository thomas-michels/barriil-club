from typing import List

from .repositories import ExtractorRepository
from .schemas import Extractor, ExtractorInDB, UpdateExtractor


class ExtractorServices:
    def __init__(self, extractor_repository: ExtractorRepository) -> None:
        self.__repository = extractor_repository

    async def create(self, extractor: Extractor) -> ExtractorInDB:
        return await self.__repository.create(extractor=extractor)

    async def update(self, id: str, extractor: UpdateExtractor) -> ExtractorInDB:
        return await self.__repository.update(id=id, extractor=extractor)

    async def search_by_id(self, id: str) -> ExtractorInDB:
        return await self.__repository.select_by_id(id=id)

    async def search_all(self) -> List[ExtractorInDB]:
        return await self.__repository.select_all()

    async def delete_by_id(self, id: str) -> bool:
        return await self.__repository.delete_by_id(id=id)
