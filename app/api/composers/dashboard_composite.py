from app.api.composers.reservation_composite import reservation_composer
from app.api.composers.keg_composite import keg_composer
from app.crud.dashboard.services import DashboardServices


async def dashboard_composer() -> DashboardServices:
    reservation_services = await reservation_composer()
    keg_services = await keg_composer()
    return DashboardServices(reservation_services, keg_services)
