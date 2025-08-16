from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.services import KegServices


async def keg_composer() -> KegServices:
    repository = KegRepository()
    services = KegServices(keg_repository=repository)
    return services
