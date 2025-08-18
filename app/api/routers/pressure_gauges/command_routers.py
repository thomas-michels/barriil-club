from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.pressure_gauge_composite import pressure_gauge_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import PressureGaugeResponse
from app.crud.pressure_gauges import (
    PressureGauge,
    UpdatePressureGauge,
    PressureGaugeServices,
)
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Pressure Gauges"])


@router.post(
    "/pressure-gauges",
    responses={201: {"model": PressureGaugeResponse}, 400: {"model": MessageResponse}},
)
async def create_pressure_gauge(
    gauge: PressureGauge,
    company: CompanyInDB = Depends(require_user_company),
    services: PressureGaugeServices = Depends(pressure_gauge_composer),
):
    gauge_in_db = await services.create(gauge=gauge, company_id=str(company.id))
    if not gauge_in_db:
        raise HTTPException(status_code=400, detail="Pressure gauge not created")
    return build_response(
        status_code=201, message="Pressure gauge created with success", data=gauge_in_db
    )


@router.put(
    "/pressure-gauges/{gauge_id}",
    responses={200: {"model": PressureGaugeResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_pressure_gauge(
    gauge_id: str,
    gauge: UpdatePressureGauge,
    services: PressureGaugeServices = Depends(pressure_gauge_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauge_in_db = await services.update(
        id=gauge_id, company_id=str(company.id), gauge=gauge
    )
    if not gauge_in_db:
        raise HTTPException(status_code=400, detail="Pressure gauge not updated")
    return build_response(
        status_code=200, message="Pressure gauge updated with success", data=gauge_in_db
    )


@router.delete(
    "/pressure-gauges/{gauge_id}",
    responses={200: {"model": PressureGaugeResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_pressure_gauge(
    gauge_id: str,
    services: PressureGaugeServices = Depends(pressure_gauge_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauge_in_db = await services.delete_by_id(id=gauge_id, company_id=str(company.id))
    if not gauge_in_db:
        raise HTTPException(status_code=400, detail="Pressure gauge not deleted")
    return build_response(
        status_code=200, message="Pressure gauge deleted with success", data=gauge_in_db
    )
