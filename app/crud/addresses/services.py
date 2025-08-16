from typing import List

import app.api.dependencies.get_address_by_zip_code as get_address_by_zip_code

from app.core.exceptions import NotFoundError, UnprocessableEntity

from .repositories import AddressRepository
from .schemas import Address, AddressInDB, UpdateAddress


class AddressServices:
    def __init__(self, address_repository: AddressRepository) -> None:
        self.__repository = address_repository

    async def create(self, address: Address) -> AddressInDB:
        return await self.__repository.create(address=address)

    async def update(self, id: str, address: UpdateAddress) -> AddressInDB:
        data = address.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(address_id=id, address=data)

    async def search_by_id(self, id: str) -> AddressInDB:
        return await self.__repository.select_by_id(id=id)

    async def search_all(self) -> List[AddressInDB]:
        return await self.__repository.select_all()

    async def delete_by_id(self, id: str) -> AddressInDB:
        return await self.__repository.delete_by_id(id=id)

    async def search_by_zip_code(self, zip_code: str) -> AddressInDB:
        address_in_db = await self.__repository.select_by_zip_code(
            zip_code=zip_code, raise_404=False
        )
        if address_in_db:
            return address_in_db

        data = get_address_by_zip_code.get_address_by_zip_code(zip_code=zip_code)
        if "erro" in data:
            raise NotFoundError(
                message=f"CEP {zip_code} not found in ViaCEP"
            )

        address_data = Address(
            postal_code=data["cep"],
            city=data["localidade"],
            district=data["bairro"],
            street=data["logradouro"],
            complement=data.get("complemento"),
            number="",
            state=data["uf"],
        )

        try:
            return await self.__repository.create(address=address_data)
        except Exception as error:
            raise UnprocessableEntity(
                message=f"Failed to create address: {str(error)}"
            )
