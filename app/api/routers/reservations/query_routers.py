from fastapi import APIRouter, Depends

from app.api.composers.reservation_composite import reservation_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from app.core.exceptions import NotFoundError
from app.core.utils.utc_datetime import UTCDateTimeType
from .schemas import ReservationResponse, ReservationListResponse
from app.crud.reservations import ReservationServices, ReservationStatus
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Reservations"])


@router.get(
    "/reservations/{reservation_id}",
    responses={200: {"model": ReservationResponse}, 404: {"model": MessageResponse}},
)
async def get_reservation_by_id(
    reservation_id: str,
    services: ReservationServices = Depends(reservation_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    reservation_in_db = await services.search_by_id(
        id=reservation_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Reservation found with success", data=reservation_in_db
    )


@router.get(
    "/reservations",
    responses={200: {"model": ReservationListResponse}},
)
async def get_reservations(
    start_date: UTCDateTimeType | None = None,
    end_date: UTCDateTimeType | None = None,
    status: ReservationStatus | None = None,
    services: ReservationServices = Depends(reservation_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    try:
        reservations = await services.search_all(
            company_id=str(company.id),
            start_date=start_date,
            end_date=end_date,
            status=status,
        )
    except NotFoundError:
        reservations = []
    return build_response(
        status_code=200,
        message="Reservations found with success",
        data=reservations,
    )
