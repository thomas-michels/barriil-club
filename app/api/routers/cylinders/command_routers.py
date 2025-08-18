from fastapi import APIRouter, Depends, HTTPException, status
from app.core.exceptions import NotFoundError

from app.api.composers.cylinder_composite import cylinder_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import CylinderResponse
from app.crud.cylinders import Cylinder, UpdateCylinder, CylinderServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Cylinders"])


@router.post(
    "/cylinders",
    responses={
        201: {"model": CylinderResponse},
        400: {"model": MessageResponse},
    },
)
async def create_cylinder(
    cylinder: Cylinder,
    company: CompanyInDB = Depends(require_user_company),
    services: CylinderServices = Depends(cylinder_composer),
):
    try:
        cylinder_in_db = await services.create(
            cylinder=cylinder, company_id=str(company.id)
        )
    except NotFoundError as error:
        raise HTTPException(status_code=400, detail=error.message)
    if not cylinder_in_db:
        raise HTTPException(status_code=400, detail="Cylinder not created")
    return build_response(
        status_code=201, message="Cylinder created with success", data=cylinder_in_db
    )


@router.put(
    "/cylinders/{cylinder_id}",
    responses={200: {"model": CylinderResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_cylinder(
    cylinder_id: str,
    cylinder: UpdateCylinder,
    services: CylinderServices = Depends(cylinder_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    cylinder_in_db = await services.update(
        id=cylinder_id, company_id=str(company.id), cylinder=cylinder
    )
    if not cylinder_in_db:
        raise HTTPException(status_code=400, detail="Cylinder not updated")
    return build_response(
        status_code=200, message="Cylinder updated with success", data=cylinder_in_db
    )


@router.delete(
    "/cylinders/{cylinder_id}",
    responses={200: {"model": CylinderResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_cylinder(
    cylinder_id: str,
    services: CylinderServices = Depends(cylinder_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    cylinder_in_db = await services.delete_by_id(
        id=cylinder_id, company_id=str(company.id)
    )
    if not cylinder_in_db:
        raise HTTPException(status_code=400, detail="Cylinder not deleted")
    return build_response(
        status_code=200, message="Cylinder deleted with success", data=cylinder_in_db
    )
