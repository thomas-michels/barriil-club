from fastapi import APIRouter, Depends, Response

from app.api.composers.extractor_composite import extractor_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import ExtractorResponse, ExtractorListResponse
from app.crud.extractors import ExtractorServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Extractors"])


@router.get(
    "/extractors/{extractor_id}",
    responses={200: {"model": ExtractorResponse}, 404: {"model": MessageResponse}},
)
async def get_extractor_by_id(
    extractor_id: str,
    extractor_services: ExtractorServices = Depends(extractor_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    extractor_in_db = await extractor_services.search_by_id(
        id=extractor_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Extractor found with success", data=extractor_in_db
    )


@router.get(
    "/extractors",
    responses={200: {"model": ExtractorListResponse}, 204: {"description": "No Content"}},
)
async def get_extractors(
    extractor_services: ExtractorServices = Depends(extractor_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    extractors = await extractor_services.search_all(company_id=str(company.id))
    if extractors:
        return build_response(
            status_code=200, message="Extractors found with success", data=extractors
        )
    return Response(status_code=204)
