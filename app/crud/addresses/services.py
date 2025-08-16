from typing import List

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
