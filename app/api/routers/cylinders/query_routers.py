from fastapi import APIRouter, Depends, Response
from app.core.exceptions import NotFoundError

from app.api.composers.cylinder_composite import cylinder_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import CylinderResponse, CylinderListResponse
from app.crud.cylinders import CylinderServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Cylinders"])


@router.get(
    "/cylinders/{cylinder_id}",
    responses={200: {"model": CylinderResponse}, 404: {"model": MessageResponse}},
)
async def get_cylinder_by_id(
    cylinder_id: str,
    services: CylinderServices = Depends(cylinder_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    cylinder_in_db = await services.search_by_id(
        id=cylinder_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200,
        message="Cylinder found with success",
        data=cylinder_in_db,
    )


@router.get(
    "/cylinders",
    responses={200: {"model": CylinderListResponse}, 204: {"description": "No Content"}},
)
async def get_cylinders(
    services: CylinderServices = Depends(cylinder_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    try:
        cylinders = await services.search_all(company_id=str(company.id))
    except NotFoundError:
        return Response(status_code=204)
    if cylinders:
        return build_response(
            status_code=200,
            message="Cylinders found with success",
            data=cylinders,
        )
    return Response(status_code=204)
