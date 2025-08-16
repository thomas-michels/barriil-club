from fastapi import APIRouter, Depends, Response

from app.api.composers.address_composite import address_composer
from app.api.dependencies import build_response
from app.api.shared_schemas.responses import MessageResponse
from .schemas import AddressResponse, AddressListResponse
from app.crud.addresses import AddressServices

router = APIRouter(tags=["Addresses"])


@router.get(
    "/addresses/{address_id}",
    responses={200: {"model": AddressResponse}, 404: {"model": MessageResponse}},
)
async def get_address_by_id(
    address_id: str,
    address_services: AddressServices = Depends(address_composer),
):
    address_in_db = await address_services.search_by_id(id=address_id)
    return build_response(
        status_code=200, message="Address found with success", data=address_in_db
    )


@router.get(
    "/addresses",
    responses={200: {"model": AddressListResponse}, 204: {"description": "No Content"}},
)
async def get_addresses(
    address_services: AddressServices = Depends(address_composer),
):
    addresses = await address_services.search_all()
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
    address_services: AddressServices = Depends(address_composer),
):
    address_in_db = await address_services.search_by_zip_code(zip_code=zip_code)
    return build_response(
        status_code=200, message="Address found with success", data=address_in_db
    )
