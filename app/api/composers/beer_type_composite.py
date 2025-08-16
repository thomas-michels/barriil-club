from app.crud.beer_types.repositories import BeerTypeRepository
from app.crud.beer_types.services import BeerTypeServices


async def beer_type_composer() -> BeerTypeServices:
    repository = BeerTypeRepository()
    services = BeerTypeServices(beer_type_repository=repository)
    return services
