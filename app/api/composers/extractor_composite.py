from app.crud.extractors.repositories import ExtractorRepository
from app.crud.extractors.services import ExtractorServices


async def extractor_composer() -> ExtractorServices:
    extractor_repository = ExtractorRepository()
    extractor_services = ExtractorServices(extractor_repository=extractor_repository)
    return extractor_services
