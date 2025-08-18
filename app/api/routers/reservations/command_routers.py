from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.reservation_composite import reservation_composer
from app.api.dependencies import build_response, require_company_member, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import ReservationResponse
from app.crud.reservations import (
    Reservation,
    UpdateReservation,
    ReservationServices,
)
from app.crud.payments.schemas import Payment
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Reservations"])


@router.post(
    "/reservations",
    responses={201: {"model": ReservationResponse}, 400: {"model": MessageResponse}},
)
async def create_reservation(
    reservation: Reservation,
    company: CompanyInDB = Depends(require_user_company),
    services: ReservationServices = Depends(reservation_composer),
):
    reservation_in_db = await services.create(
        reservation=reservation, company_id=str(company.id)
    )
    if not reservation_in_db:
        raise HTTPException(status_code=400, detail="Reservation not created")
    return build_response(
        status_code=201, message="Reservation created with success", data=reservation_in_db
    )


@router.put(
    "/reservations/{reservation_id}",
    responses={200: {"model": ReservationResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_reservation(
    reservation_id: str,
    reservation: UpdateReservation,
    services: ReservationServices = Depends(reservation_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    reservation_in_db = await services.update(
        id=reservation_id, company_id=str(company.id), reservation=reservation
    )
    if not reservation_in_db:
        raise HTTPException(status_code=400, detail="Reservation not updated")
    return build_response(
        status_code=200, message="Reservation updated with success", data=reservation_in_db
    )


@router.delete(
    "/reservations/{reservation_id}",
    responses={200: {"model": ReservationResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_reservation(
    reservation_id: str,
    services: ReservationServices = Depends(reservation_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    reservation_in_db = await services.delete_by_id(
        id=reservation_id, company_id=str(company.id)
    )
    if not reservation_in_db:
        raise HTTPException(status_code=400, detail="Reservation not deleted")
    return build_response(
        status_code=200, message="Reservation deleted with success", data=reservation_in_db
    )


@router.post(
    "/reservations/{reservation_id}/payments",
    responses={200: {"model": ReservationResponse}, 404: {"model": MessageResponse}},
)
async def add_reservation_payment(
    reservation_id: str,
    payment: Payment,
    services: ReservationServices = Depends(reservation_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    reservation_in_db = await services.add_payment(
        id=reservation_id, company_id=str(company.id), payment=payment
    )
    return build_response(
        status_code=200,
        message="Reservation payment added with success",
        data=reservation_in_db,
    )


@router.put(
    "/reservations/{reservation_id}/payments/{payment_index}",
    responses={200: {"model": ReservationResponse}, 404: {"model": MessageResponse}},
)
async def update_reservation_payment(
    reservation_id: str,
    payment_index: int,
    payment: Payment,
    services: ReservationServices = Depends(reservation_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    reservation_in_db = await services.update_payment(
        id=reservation_id,
        company_id=str(company.id),
        index=payment_index,
        payment=payment,
    )
    return build_response(
        status_code=200,
        message="Reservation payment updated with success",
        data=reservation_in_db,
    )


@router.delete(
    "/reservations/{reservation_id}/payments/{payment_index}",
    responses={200: {"model": ReservationResponse}, 404: {"model": MessageResponse}},
)
async def delete_reservation_payment(
    reservation_id: str,
    payment_index: int,
    services: ReservationServices = Depends(reservation_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    reservation_in_db = await services.delete_payment(
        id=reservation_id, company_id=str(company.id), index=payment_index
    )
    return build_response(
        status_code=200,
        message="Reservation payment deleted with success",
        data=reservation_in_db,
    )
