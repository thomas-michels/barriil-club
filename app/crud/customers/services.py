from typing import List

from .repositories import CustomerRepository
from .schemas import Customer, CustomerInDB, UpdateCustomer


class CustomerServices:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.__repository = customer_repository

    async def create(self, customer: Customer) -> CustomerInDB:
        return await self.__repository.create(customer=customer)

    async def update(self, id: str, customer: UpdateCustomer) -> CustomerInDB:
        data = customer.model_dump(exclude_unset=True, exclude_none=True)
        return await self.__repository.update(customer_id=id, customer=data)

    async def search_by_id(self, id: str) -> CustomerInDB:
        return await self.__repository.select_by_id(id=id)

    async def search_all(self) -> List[CustomerInDB]:
        return await self.__repository.select_all()

    async def delete_by_id(self, id: str) -> CustomerInDB:
        return await self.__repository.delete_by_id(id=id)
