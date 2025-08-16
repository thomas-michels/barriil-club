from app.crud.customers.repositories import CustomerRepository
from app.crud.customers.services import CustomerServices


async def customer_composer() -> CustomerServices:
    customer_repository = CustomerRepository()
    customer_services = CustomerServices(customer_repository=customer_repository)
    return customer_services
