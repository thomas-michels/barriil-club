from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.crud.pressure_gauges.services import PressureGaugeServices


async def pressure_gauge_composer() -> PressureGaugeServices:
    repository = PressureGaugeRepository()
    services = PressureGaugeServices(repository=repository)
    return services
