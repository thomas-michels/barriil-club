from fastapi import APIRouter, Depends, Response

from app.api.composers.pressure_gauge_composite import pressure_gauge_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import PressureGaugeResponse, PressureGaugeListResponse
from app.crud.pressure_gauges import PressureGaugeServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Pressure Gauges"])


@router.get(
    "/pressure-gauges/{gauge_id}",
    responses={200: {"model": PressureGaugeResponse}, 404: {"model": MessageResponse}},
)
async def get_pressure_gauge_by_id(
    gauge_id: str,
    services: PressureGaugeServices = Depends(pressure_gauge_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauge_in_db = await services.search_by_id(id=gauge_id, company_id=str(company.id))
    return build_response(
        status_code=200,
        message="Pressure gauge found with success",
        data=gauge_in_db,
    )


@router.get(
    "/pressure-gauges",
    responses={200: {"model": PressureGaugeListResponse}, 204: {"description": "No Content"}},
)
async def get_pressure_gauges(
    services: PressureGaugeServices = Depends(pressure_gauge_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauges = await services.search_all(company_id=str(company.id))
    if gauges:
        return build_response(
            status_code=200,
            message="Pressure gauges found with success",
            data=gauges,
        )
    return Response(status_code=204)
