from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.cylinders.repositories import CylinderRepository
from app.crud.extraction_kits.repositories import ExtractionKitRepository
from app.crud.kegs.repositories import KegRepository
from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.services import ReservationServices


async def reservation_composer() -> ReservationServices:
    repository = ReservationRepository()
    keg_repo = KegRepository()
    pg_repo = ExtractionKitRepository()
    cylinder_repo = CylinderRepository()
    dispenser_repo = BeerDispenserRepository()
    services = ReservationServices(
        reservation_repository=repository,
        keg_repository=keg_repo,
        extraction_kit_repository=pg_repo,
        cylinder_repository=cylinder_repo,
        beer_dispenser_repository=dispenser_repo,
    )
    return services
