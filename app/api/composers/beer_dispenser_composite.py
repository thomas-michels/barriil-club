from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.beer_dispensers.services import BeerDispenserServices
from app.crud.reservations.repositories import ReservationRepository


async def beer_dispenser_composer() -> BeerDispenserServices:
    repository = BeerDispenserRepository()
    reservation_repository = ReservationRepository()
    services = BeerDispenserServices(
        repository=repository, reservation_repository=reservation_repository
    )
    return services
