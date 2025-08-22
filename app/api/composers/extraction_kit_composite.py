from app.crud.extraction_kits.repositories import ExtractionKitRepository
from app.crud.extraction_kits.services import ExtractionKitServices


async def extraction_kit_composer() -> ExtractionKitServices:
    repository = ExtractionKitRepository()
    services = ExtractionKitServices(repository=repository)
    return services
