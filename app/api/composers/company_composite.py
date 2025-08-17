from app.crud.companies.repositories import CompanyRepository
from app.crud.addresses.repositories import AddressRepository
from app.crud.companies.services import CompanyServices


async def company_composer() -> CompanyServices:
    company_repository = CompanyRepository()
    address_repository = AddressRepository()
    company_services = CompanyServices(
        company_repository=company_repository,
        address_repository=address_repository,
    )
    return company_services
