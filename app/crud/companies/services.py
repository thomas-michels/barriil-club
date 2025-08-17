from typing import List

from app.crud.addresses.repositories import AddressRepository
from .repositories import CompanyRepository
from .schemas import Company, CompanyInDB, UpdateCompany, CompanyMember


class CompanyServices:
    def __init__(
        self,
        company_repository: CompanyRepository,
        address_repository: AddressRepository,
    ) -> None:
        self.__repository = company_repository
        self.__address_repository = address_repository

    async def create(self, company: Company) -> CompanyInDB:
        if company.address_id is not None:
            await self.__address_repository.select_active_by_id(company.address_id)
        return await self.__repository.create(company=company)

    async def update(self, id: str, company: UpdateCompany) -> CompanyInDB:
        data = company.model_dump(exclude_unset=True, exclude_none=True)
        address_id = data.get("address_id")
        if address_id is not None:
            await self.__address_repository.select_active_by_id(address_id)
        return await self.__repository.update(company_id=id, company=data)

    async def search_by_id(self, id: str) -> CompanyInDB:
        return await self.__repository.select_by_id(id=id)

    async def search_all(self) -> List[CompanyInDB]:
        return await self.__repository.select_all()

    async def delete_by_id(self, id: str) -> CompanyInDB:
        return await self.__repository.delete_by_id(id=id)

    async def add_member(self, company_id: str, member: CompanyMember) -> CompanyInDB:
        return await self.__repository.add_member(company_id=company_id, member=member)

    async def search_by_user(self, user_id: str) -> CompanyInDB:
        return await self.__repository.select_by_user(user_id=user_id)
