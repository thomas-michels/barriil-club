from fastapi import APIRouter, Depends

from app.api.composers.beer_type_composite import beer_type_composer
from app.api.dependencies import build_response, require_user_company
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
    company: CompanyInDB = Depends(require_user_company),
    services: BeerTypeServices = Depends(beer_type_composer),
):
    beer_type_in_db = await services.search_by_id(
        id=beer_type_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Beer type found with success", data=beer_type_in_db
    )


@router.get(
    "/beer-types",
    responses={200: {"model": BeerTypeListResponse}},
)
async def get_beer_types(
    services: BeerTypeServices = Depends(beer_type_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    beer_types = await services.search_all(company_id=str(company.id))
    return build_response(
        status_code=200,
        message="Beer types found with success",
        data=beer_types or [],
    )
