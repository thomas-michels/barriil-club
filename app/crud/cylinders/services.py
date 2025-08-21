from typing import List

from .repositories import CylinderRepository
from .schemas import Cylinder, CylinderInDB, UpdateCylinder
from .models import CylinderModel


class CylinderServices:
    def __init__(self, repository: CylinderRepository) -> None:
        self.__repository = repository

    async def create(self, cylinder: Cylinder, company_id: str) -> CylinderInDB:
        existing = CylinderModel.objects(
            number__startswith=cylinder.number, company_id=company_id
        ).count()
        if existing > 0:
            cylinder.number = f"{cylinder.number}{existing}"
        return await self.__repository.create(cylinder=cylinder, company_id=company_id)

    async def update(
        self, id: str, company_id: str, cylinder: UpdateCylinder
    ) -> CylinderInDB:
        data = cylinder.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(
            cylinder_id=id, company_id=company_id, cylinder=data
        )

    async def search_by_id(self, id: str, company_id: str) -> CylinderInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    async def search_all(self, company_id: str) -> List[CylinderInDB]:
        return await self.__repository.select_all(company_id=company_id)

    async def delete_by_id(self, id: str, company_id: str) -> CylinderInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)
