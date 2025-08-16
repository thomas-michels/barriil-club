from datetime import date

from fastapi import APIRouter, Depends, Response

from app.api.composers.reservation_composite import reservation_composer
from app.api.dependencies import build_response, require_company_member
from app.api.shared_schemas.responses import MessageResponse
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
    company_id: str,
    services: ReservationServices = Depends(reservation_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    reservation_in_db = await services.search_by_id(id=reservation_id, company_id=company_id)
    return build_response(
        status_code=200, message="Reservation found with success", data=reservation_in_db
    )


@router.get(
    "/reservations",
    responses={200: {"model": ReservationListResponse}, 204: {"description": "No Content"}},
)
async def get_reservations(
    company_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    status: ReservationStatus | None = None,
    services: ReservationServices = Depends(reservation_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    reservations = await services.search_all(
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )
    if reservations:
        return build_response(
            status_code=200,
            message="Reservations found with success",
            data=reservations,
        )
    return Response(status_code=204)
