from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.keg_composite import keg_composer
from app.api.dependencies import build_response, require_company_member, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import KegResponse
from app.crud.kegs import Keg, UpdateKeg, KegServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Kegs"])


@router.post(
    "/kegs",
    responses={201: {"model": KegResponse}, 400: {"model": MessageResponse}},
)
async def create_keg(
    keg: Keg,
    company: CompanyInDB = Depends(require_user_company),
    services: KegServices = Depends(keg_composer),
):
    if keg.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to use this company",
        )
    keg_in_db = await services.create(keg=keg)
    if not keg_in_db:
        raise HTTPException(status_code=400, detail="Keg not created")
    return build_response(
        status_code=201, message="Keg created with success", data=keg_in_db
    )


@router.put(
    "/kegs/{keg_id}",
    responses={200: {"model": KegResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_keg(
    keg_id: str,
    company_id: str,
    keg: UpdateKeg,
    services: KegServices = Depends(keg_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    keg_in_db = await services.update(id=keg_id, company_id=company_id, keg=keg)
    if not keg_in_db:
        raise HTTPException(status_code=400, detail="Keg not updated")
    return build_response(
        status_code=200, message="Keg updated with success", data=keg_in_db
    )


@router.delete(
    "/kegs/{keg_id}",
    responses={200: {"model": KegResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_keg(
    keg_id: str,
    company_id: str,
    services: KegServices = Depends(keg_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    keg_in_db = await services.delete_by_id(id=keg_id, company_id=company_id)
    if not keg_in_db:
        raise HTTPException(status_code=400, detail="Keg not deleted")
    return build_response(
        status_code=200, message="Keg deleted with success", data=keg_in_db
    )
