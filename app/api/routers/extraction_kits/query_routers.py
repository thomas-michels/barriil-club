from fastapi import APIRouter, Depends

from app.api.composers.extraction_kit_composite import extraction_kit_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from app.crud.companies.schemas import CompanyInDB
from app.crud.extraction_kits import ExtractionKitServices

from .schemas import ExtractionKitListResponse, ExtractionKitResponse

router = APIRouter(tags=["Extraction Kits"])


@router.get(
    "/extraction-kits/{gauge_id}",
    responses={200: {"model": ExtractionKitResponse}, 404: {"model": MessageResponse}},
)
async def get_extraction_kit_by_id(
    gauge_id: str,
    services: ExtractionKitServices = Depends(extraction_kit_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauge_in_db = await services.search_by_id(id=gauge_id, company_id=str(company.id))
    return build_response(
        status_code=200,
        message="Extraction kit found with success",
        data=gauge_in_db,
    )


@router.get(
    "/extraction-kits",
    responses={200: {"model": ExtractionKitListResponse}},
)
async def get_extraction_kits(
    services: ExtractionKitServices = Depends(extraction_kit_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    gauges = await services.search_all(company_id=str(company.id))
    return build_response(
        status_code=200,
        message="Extraction kits found with success",
        data=gauges or [],
    )
