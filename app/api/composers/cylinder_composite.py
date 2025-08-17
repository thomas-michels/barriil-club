from app.crud.cylinders.repositories import CylinderRepository
from app.crud.cylinders.services import CylinderServices


async def cylinder_composer() -> CylinderServices:
    repository = CylinderRepository()
    services = CylinderServices(repository=repository)
    return services
