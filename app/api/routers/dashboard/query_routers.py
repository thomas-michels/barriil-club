from fastapi import APIRouter, Depends, Response

from app.api.composers.dashboard_composite import dashboard_composer
from app.api.dependencies import build_response, require_user_company
from app.api.routers.reservations.schemas import ReservationListResponse
from app.crud.dashboard.services import DashboardServices
from app.crud.companies.schemas import CompanyInDB

from .schemas import MonthlyRevenueResponse, ReservationCalendarResponse

router = APIRouter(tags=["Dashboard"])


@router.get(
    "/dashboard/revenue",
    responses={200: {"model": MonthlyRevenueResponse}},
)
async def get_monthly_revenue(
    year: int | None = None,
    services: DashboardServices = Depends(dashboard_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    from app.core.utils.utc_datetime import UTCDateTime

    year = year or UTCDateTime.now().year
    revenue = await services.monthly_revenue(company_id=str(company.id), year=year)
    return build_response(
        status_code=200,
        message="Monthly revenue found with success",
        data=revenue,
    )


@router.get(
    "/dashboard/upcoming-reservations",
    responses={200: {"model": ReservationListResponse}, 204: {"description": "No Content"}},
)
async def get_upcoming_reservations(
    services: DashboardServices = Depends(dashboard_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    reservations = await services.upcoming_reservations(company_id=str(company.id))
    if reservations:
        return build_response(
            status_code=200,
            message="Reservations found with success",
            data=reservations,
        )
    return Response(status_code=204)


@router.get(
    "/dashboard/calendar",
    responses={200: {"model": ReservationCalendarResponse}},
)
async def get_reservation_calendar(
    year: int,
    month: int,
    services: DashboardServices = Depends(dashboard_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    calendar_data = await services.reservation_calendar(
        company_id=str(company.id), year=year, month=month
    )
    return build_response(
        status_code=200,
        message="Reservation calendar found with success",
        data=calendar_data,
    )
