from fastapi import APIRouter, Depends

from app.api.composers.keg_composite import keg_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import KegResponse, KegListResponse
from app.crud.kegs import KegServices, KegStatus
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Kegs"])


@router.get(
    "/kegs/{keg_id}",
    responses={200: {"model": KegResponse}, 404: {"model": MessageResponse}},
)
async def get_keg_by_id(
    keg_id: str,
    company: CompanyInDB = Depends(require_user_company),
    services: KegServices = Depends(keg_composer),
):
    keg_in_db = await services.search_by_id(id=keg_id, company_id=str(company.id))
    return build_response(
        status_code=200, message="Keg found with success", data=keg_in_db
    )


@router.get(
    "/kegs",
    responses={200: {"model": KegListResponse}},
)
async def get_kegs(
    status: KegStatus | None = None,
    services: KegServices = Depends(keg_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    kegs = await services.search_all(company_id=str(company.id), status=status)
    return build_response(
        status_code=200, message="Kegs found with success", data=kegs or []
    )
