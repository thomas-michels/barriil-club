from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.beer_type_composite import beer_type_composer
from app.api.dependencies import build_response, require_company_member, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import BeerTypeResponse
from app.crud.beer_types import BeerType, UpdateBeerType, BeerTypeServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Beer Types"])


@router.post(
    "/beer-types",
    responses={201: {"model": BeerTypeResponse}, 400: {"model": MessageResponse}},
)
async def create_beer_type(
    beer_type: BeerType,
    company: CompanyInDB = Depends(require_user_company),
    services: BeerTypeServices = Depends(beer_type_composer),
):
    if beer_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to use this company",
        )
    beer_type_in_db = await services.create(beer_type=beer_type)
    if not beer_type_in_db:
        raise HTTPException(status_code=400, detail="Beer type not created")
    return build_response(
        status_code=201, message="Beer type created with success", data=beer_type_in_db
    )


@router.put(
    "/beer-types/{beer_type_id}",
    responses={200: {"model": BeerTypeResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_beer_type(
    beer_type_id: str,
    company_id: str,
    beer_type: UpdateBeerType,
    services: BeerTypeServices = Depends(beer_type_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    beer_type_in_db = await services.update(
        id=beer_type_id, company_id=company_id, beer_type=beer_type
    )
    if not beer_type_in_db:
        raise HTTPException(status_code=400, detail="Beer type not updated")
    return build_response(
        status_code=200, message="Beer type updated with success", data=beer_type_in_db
    )


@router.delete(
    "/beer-types/{beer_type_id}",
    responses={200: {"model": BeerTypeResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_beer_type(
    beer_type_id: str,
    company_id: str,
    services: BeerTypeServices = Depends(beer_type_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    beer_type_in_db = await services.delete_by_id(
        id=beer_type_id, company_id=company_id
    )
    if not beer_type_in_db:
        raise HTTPException(status_code=400, detail="Beer type not deleted")
    return build_response(
        status_code=200, message="Beer type deleted with success", data=beer_type_in_db
    )
