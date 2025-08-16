from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.services import ReservationServices
from app.crud.kegs.repositories import KegRepository
from app.crud.pressure_gauges.repositories import PressureGaugeRepository


async def reservation_composer() -> ReservationServices:
    repository = ReservationRepository()
    keg_repo = KegRepository()
    pg_repo = PressureGaugeRepository()
    services = ReservationServices(
        reservation_repository=repository,
        keg_repository=keg_repo,
        pressure_gauge_repository=pg_repo,
    )
    return services
