from typing import List

import app.api.dependencies.get_address_by_zip_code as get_address_by_zip_code

from app.core.exceptions import NotFoundError

from .repositories import AddressRepository
from .schemas import Address, AddressInDB, UpdateAddress


class AddressServices:
    def __init__(self, address_repository: AddressRepository) -> None:
        self.__repository = address_repository

    async def create(self, address: Address, company_id: str) -> AddressInDB:
        return await self.__repository.create(address=address, company_id=company_id)

    async def update(
        self, id: str, company_id: str, address: UpdateAddress
    ) -> AddressInDB:
        data = address.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(
            address_id=id, company_id=company_id, address=data
        )

    async def search_by_id(self, id: str, company_id: str) -> AddressInDB:
        return await self.__repository.select_by_id(id=id, company_id=company_id)

    async def search_all(self, company_id: str) -> List[AddressInDB]:
        return await self.__repository.select_all(company_id=company_id)

    async def delete_by_id(self, id: str, company_id: str) -> AddressInDB:
        return await self.__repository.delete_by_id(id=id, company_id=company_id)

    async def search_by_zip_code(self, zip_code: str, company_id: str) -> Address:
        """Fetch address information directly from ViaCEP service.

        This method ignores any address stored in the local database and
        always retrieves fresh data from ViaCEP.
        """

        data = get_address_by_zip_code.get_address_by_zip_code(zip_code=zip_code)

        if "erro" in data:
            raise NotFoundError(message=f"CEP {zip_code} not found in ViaCEP")

        return Address(
            postal_code=data["cep"],
            city=data["localidade"],
            district=data["bairro"],
            street=data["logradouro"],
            complement=data.get("complemento"),
            number="",
            state=data["uf"],
            reference=None,
        )
