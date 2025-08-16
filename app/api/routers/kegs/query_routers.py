from fastapi import APIRouter, Depends, Response

from app.api.composers.keg_composite import keg_composer
from app.api.dependencies import build_response, require_company_member
from app.api.shared_schemas.responses import MessageResponse
from .schemas import KegResponse, KegListResponse
from app.crud.kegs import KegServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Kegs"])


@router.get(
    "/kegs/{keg_id}",
    responses={200: {"model": KegResponse}, 404: {"model": MessageResponse}},
)
async def get_keg_by_id(
    keg_id: str,
    company_id: str,
    services: KegServices = Depends(keg_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    keg_in_db = await services.search_by_id(id=keg_id, company_id=company_id)
    return build_response(
        status_code=200, message="Keg found with success", data=keg_in_db
    )


@router.get(
    "/kegs",
    responses={200: {"model": KegListResponse}, 204: {"description": "No Content"}},
)
async def get_kegs(
    company_id: str,
    services: KegServices = Depends(keg_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    kegs = await services.search_all(company_id=company_id)
    if kegs:
        return build_response(
            status_code=200, message="Kegs found with success", data=kegs
        )
    return Response(status_code=204)
