from app.crud.reservations.repositories import ReservationRepository
from app.crud.customers.repositories import CustomerRepository
from app.crud.payments.services import PaymentServices


async def payment_composer() -> PaymentServices:
    reservation_repo = ReservationRepository()
    customer_repo = CustomerRepository()
    services = PaymentServices(
        reservation_repository=reservation_repo,
        customer_repository=customer_repo,
    )
    return services
