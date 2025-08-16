from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices


async def company_composer() -> CompanyServices:
    company_repository = CompanyRepository()
    company_services = CompanyServices(company_repository=company_repository)
    return company_services
