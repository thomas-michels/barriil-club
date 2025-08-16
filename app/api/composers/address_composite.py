from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.services import AddressServices


async def address_composer() -> AddressServices:
    address_repository = AddressRepository()
    address_services = AddressServices(address_repository=address_repository)
    return address_services
