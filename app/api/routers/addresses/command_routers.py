from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.address_composite import address_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import AddressResponse
from app.crud.addresses import Address, UpdateAddress, AddressServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Addresses"])


@router.post(
    "/addresses",
    responses={201: {"model": AddressResponse}, 400: {"model": MessageResponse}},
)
async def create_address(
    address: Address,
    company: CompanyInDB = Depends(require_user_company),
    address_services: AddressServices = Depends(address_composer),
):
    address_in_db = await address_services.create(
        address=address, company_id=str(company.id)
    )
    if not address_in_db:
        raise HTTPException(status_code=400, detail="Address not created")
    return build_response(
        status_code=201, message="Address created with success", data=address_in_db
    )


@router.put(
    "/addresses/{address_id}",
    responses={200: {"model": AddressResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_address(
    address_id: str,
    address: UpdateAddress,
    address_services: AddressServices = Depends(address_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    address_in_db = await address_services.update(
        id=address_id, company_id=str(company.id), address=address
    )
    if not address_in_db:
        raise HTTPException(status_code=400, detail="Address not updated")
    return build_response(
        status_code=200, message="Address updated with success", data=address_in_db
    )


@router.delete(
    "/addresses/{address_id}",
    responses={200: {"model": AddressResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_address(
    address_id: str,
    address_services: AddressServices = Depends(address_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    address_in_db = await address_services.delete_by_id(
        id=address_id, company_id=str(company.id)
    )
    if not address_in_db:
        raise HTTPException(status_code=400, detail="Address not deleted")
    return build_response(
        status_code=200, message="Address deleted with success", data=address_in_db
    )
