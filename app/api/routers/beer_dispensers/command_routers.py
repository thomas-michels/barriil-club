from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.beer_dispenser_composite import beer_dispenser_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import BeerDispenserResponse
from app.crud.beer_dispensers import (
    BeerDispenser,
    UpdateBeerDispenser,
    BeerDispenserServices,
)
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Beer Dispensers"])


@router.post(
    "/beer-dispensers",
    responses={201: {"model": BeerDispenserResponse}, 400: {"model": MessageResponse}},
)
async def create_beer_dispenser(
    dispenser: BeerDispenser,
    company: CompanyInDB = Depends(require_user_company),
    services: BeerDispenserServices = Depends(beer_dispenser_composer),
):
    dispenser_in_db = await services.create(
        dispenser=dispenser, company_id=str(company.id)
    )
    if not dispenser_in_db:
        raise HTTPException(status_code=400, detail="Chopeira não criada")
    return build_response(
        status_code=201, message="Beer dispenser created with success", data=dispenser_in_db
    )


@router.put(
    "/beer-dispensers/{dispenser_id}",
    responses={200: {"model": BeerDispenserResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_beer_dispenser(
    dispenser_id: str,
    dispenser: UpdateBeerDispenser,
    services: BeerDispenserServices = Depends(beer_dispenser_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    dispenser_in_db = await services.update(
        id=dispenser_id, company_id=str(company.id), dispenser=dispenser
    )
    if not dispenser_in_db:
        raise HTTPException(status_code=400, detail="Chopeira não atualizada")
    return build_response(
        status_code=200, message="Beer dispenser updated with success", data=dispenser_in_db
    )


@router.delete(
    "/beer-dispensers/{dispenser_id}",
    responses={200: {"model": BeerDispenserResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_beer_dispenser(
    dispenser_id: str,
    services: BeerDispenserServices = Depends(beer_dispenser_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    dispenser_in_db = await services.delete_by_id(
        id=dispenser_id, company_id=str(company.id)
    )
    if not dispenser_in_db:
        raise HTTPException(status_code=400, detail="Chopeira não excluída")
    return build_response(
        status_code=200, message="Beer dispenser deleted with success", data=dispenser_in_db
    )
