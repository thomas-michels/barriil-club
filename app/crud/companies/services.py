from typing import List

from .repositories import CompanyRepository
from .schemas import Company, CompanyInDB, UpdateCompany, CompanyMember


class CompanyServices:
    def __init__(self, company_repository: CompanyRepository) -> None:
        self.__repository = company_repository

    async def create(self, company: Company) -> CompanyInDB:
        return await self.__repository.create(company=company)

    async def update(self, id: str, company: UpdateCompany) -> CompanyInDB:
        return await self.__repository.update(id=id, company=company)

    async def search_by_id(self, id: str) -> CompanyInDB:
        return await self.__repository.select_by_id(id=id)

    async def search_all(self) -> List[CompanyInDB]:
        return await self.__repository.select_all()

    async def delete_by_id(self, id: str) -> bool:
        return await self.__repository.delete_by_id(id=id)

    async def add_member(self, company_id: str, member: CompanyMember) -> CompanyInDB:
        return await self.__repository.add_member(company_id=company_id, member=member)
