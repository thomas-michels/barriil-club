from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.extractor_composite import extractor_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import ExtractorResponse
from app.crud.extractors import Extractor, UpdateExtractor, ExtractorServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Extractors"])


@router.post(
    "/extractors",
    responses={201: {"model": ExtractorResponse}},
)
async def create_extractor(
    extractor: Extractor,
    company: CompanyInDB = Depends(require_user_company),
    extractor_services: ExtractorServices = Depends(extractor_composer),
):
    extractor_in_db = await extractor_services.create(
        extractor=extractor, company_id=str(company.id)
    )
    return build_response(
        status_code=201, message="Extractor created with success", data=extractor_in_db
    )


@router.put(
    "/extractors/{extractor_id}",
    responses={200: {"model": ExtractorResponse}, 404: {"model": MessageResponse}},
)
async def update_extractor(
    extractor_id: str,
    extractor: UpdateExtractor,
    extractor_services: ExtractorServices = Depends(extractor_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    extractor_in_db = await extractor_services.update(
        id=extractor_id, company_id=str(company.id), extractor=extractor
    )
    return build_response(
        status_code=200, message="Extractor updated with success", data=extractor_in_db
    )


@router.delete(
    "/extractors/{extractor_id}",
    responses={200: {"model": ExtractorResponse}, 404: {"model": MessageResponse}},
)
async def delete_extractor(
    extractor_id: str,
    extractor_services: ExtractorServices = Depends(extractor_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    extractor_in_db = await extractor_services.delete_by_id(
        id=extractor_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Extractor deleted with success", data=extractor_in_db
    )
