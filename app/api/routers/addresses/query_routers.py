from fastapi import APIRouter, Depends, Response

from app.api.composers.address_composite import address_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import AddressResponse, AddressListResponse
from app.crud.addresses import AddressServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Addresses"])


@router.get(
    "/addresses/{address_id}",
    responses={200: {"model": AddressResponse}, 404: {"model": MessageResponse}},
)
async def get_address_by_id(
    address_id: str,
    company: CompanyInDB = Depends(require_user_company),
    address_services: AddressServices = Depends(address_composer),
):
    address_in_db = await address_services.search_by_id(
        id=address_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Address found with success", data=address_in_db
    )


@router.get(
    "/addresses",
    responses={200: {"model": AddressListResponse}, 204: {"description": "No Content"}},
)
async def get_addresses(
    address_services: AddressServices = Depends(address_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    addresses = await address_services.search_all(company_id=str(company.id))
    if addresses:
        return build_response(
            status_code=200, message="Addresses found with success", data=addresses
        )
    return Response(status_code=204)


@router.get(
    "/addresses/zip/{zip_code}",
    responses={200: {"model": AddressResponse}, 404: {"model": MessageResponse}},
)
async def get_address_by_zip_code(
    zip_code: str,
    company: CompanyInDB = Depends(require_user_company),
    address_services: AddressServices = Depends(address_composer),
):
    address_in_db = await address_services.search_by_zip_code(
        zip_code=zip_code, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Address found with success", data=address_in_db
    )
