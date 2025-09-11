from fastapi import APIRouter, Depends, HTTPException

from app.api.composers.extraction_kit_composite import extraction_kit_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from app.crud.companies.schemas import CompanyInDB
from app.crud.extraction_kits import (
    ExtractionKit,
    ExtractionKitServices,
    UpdateExtractionKit,
)

from .schemas import ExtractionKitResponse

router = APIRouter(tags=["Extraction Kits"])


@router.post(
    "/extraction-kits",
    responses={201: {"model": ExtractionKitResponse}, 400: {"model": MessageResponse}},
)
async def create_extraction_kit(
    gauge: ExtractionKit,
    company: CompanyInDB = Depends(require_user_company),
    services: ExtractionKitServices = Depends(extraction_kit_composer),
):
    gauge_in_db = await services.create(gauge=gauge, company_id=str(company.id))
    if not gauge_in_db:
        raise HTTPException(status_code=400, detail="Kit de extração não criado")
    return build_response(
        status_code=201, message="Extraction kit created with success", data=gauge_in_db
    )


@router.put(
    "/extraction-kits/{gauge_id}",
    responses={
        200: {"model": ExtractionKitResponse},
        400: {"model": MessageResponse},
        404: {"model": MessageResponse},
    },
)
async def update_extraction_kit(
    gauge_id: str,
    gauge: UpdateExtractionKit,
    services: ExtractionKitServices = Depends(extraction_kit_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauge_in_db = await services.update(
        id=gauge_id, company_id=str(company.id), gauge=gauge
    )
    if not gauge_in_db:
        raise HTTPException(status_code=400, detail="Kit de extração não atualizado")
    return build_response(
        status_code=200, message="Extraction kit updated with success", data=gauge_in_db
    )


@router.delete(
    "/extraction-kits/{gauge_id}",
    responses={
        200: {"model": ExtractionKitResponse},
        400: {"model": MessageResponse},
        404: {"model": MessageResponse},
    },
)
async def delete_extraction_kit(
    gauge_id: str,
    services: ExtractionKitServices = Depends(extraction_kit_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauge_in_db = await services.delete_by_id(id=gauge_id, company_id=str(company.id))
    if not gauge_in_db:
        raise HTTPException(status_code=400, detail="Kit de extração não excluído")
    return build_response(
        status_code=200, message="Extraction kit deleted with success", data=gauge_in_db
    )
