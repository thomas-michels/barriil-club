from fastapi import APIRouter, Depends, Response

from app.api.composers.extractor_composite import extractor_composer
from app.api.dependencies import build_response
from app.api.shared_schemas.responses import MessageResponse
from .schemas import ExtractorResponse, ExtractorListResponse
from app.crud.extractors import ExtractorServices

router = APIRouter(tags=["Extractors"])


@router.get(
    "/extractors/{extractor_id}",
    responses={200: {"model": ExtractorResponse}, 404: {"model": MessageResponse}},
)
async def get_extractor_by_id(
    extractor_id: str,
    company_id: str,
    extractor_services: ExtractorServices = Depends(extractor_composer),
):
    extractor_in_db = await extractor_services.search_by_id(
        id=extractor_id, company_id=company_id
    )
    return build_response(
        status_code=200, message="Extractor found with success", data=extractor_in_db
    )


@router.get(
    "/extractors",
    responses={200: {"model": ExtractorListResponse}, 204: {"description": "No Content"}},
)
async def get_extractors(
    company_id: str,
    extractor_services: ExtractorServices = Depends(extractor_composer),
):
    extractors = await extractor_services.search_all(company_id=company_id)
    if extractors:
        return build_response(
            status_code=200, message="Extractors found with success", data=extractors
        )
    return Response(status_code=204)
