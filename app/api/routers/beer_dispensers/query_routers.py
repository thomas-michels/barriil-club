from fastapi import APIRouter, Depends

from app.api.composers.beer_dispenser_composite import beer_dispenser_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import BeerDispenserResponse, BeerDispenserListResponse
from app.crud.beer_dispensers import BeerDispenserServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Beer Dispensers"])


@router.get(
    "/beer-dispensers/{dispenser_id}",
    responses={200: {"model": BeerDispenserResponse}, 404: {"model": MessageResponse}},
)
async def get_beer_dispenser_by_id(
    dispenser_id: str,
    services: BeerDispenserServices = Depends(beer_dispenser_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    dispenser_in_db = await services.search_by_id(
        id=dispenser_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Beer dispenser found with success", data=dispenser_in_db
    )


@router.get(
    "/beer-dispensers",
    responses={200: {"model": BeerDispenserListResponse}},
)
async def get_beer_dispensers(
    services: BeerDispenserServices = Depends(beer_dispenser_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    dispensers = await services.search_all(company_id=str(company.id))
    return build_response(
        status_code=200,
        message="Beer dispensers found with success",
        data=dispensers or [],
    )
