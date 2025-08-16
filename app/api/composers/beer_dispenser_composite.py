from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.beer_dispensers.services import BeerDispenserServices


async def beer_dispenser_composer() -> BeerDispenserServices:
    repository = BeerDispenserRepository()
    services = BeerDispenserServices(repository=repository)
    return services
