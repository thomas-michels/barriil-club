from fastapi import APIRouter, Depends, Response

from app.api.composers.beer_type_composite import beer_type_composer
from app.api.dependencies import build_response, require_company_member
from app.api.shared_schemas.responses import MessageResponse
from .schemas import BeerTypeResponse, BeerTypeListResponse
from app.crud.beer_types import BeerTypeServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Beer Types"])


@router.get(
    "/beer-types/{beer_type_id}",
    responses={200: {"model": BeerTypeResponse}, 404: {"model": MessageResponse}},
)
async def get_beer_type_by_id(
    beer_type_id: str,
    company_id: str,
    services: BeerTypeServices = Depends(beer_type_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    beer_type_in_db = await services.search_by_id(
        id=beer_type_id, company_id=company_id
    )
    return build_response(
        status_code=200, message="Beer type found with success", data=beer_type_in_db
    )


@router.get(
    "/beer-types",
    responses={200: {"model": BeerTypeListResponse}, 204: {"description": "No Content"}},
)
async def get_beer_types(
    company_id: str,
    services: BeerTypeServices = Depends(beer_type_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    beer_types = await services.search_all(company_id=company_id)
    if beer_types:
        return build_response(
            status_code=200, message="Beer types found with success", data=beer_types
        )
    return Response(status_code=204)
