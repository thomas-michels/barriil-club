from fastapi import APIRouter, Depends, Response

from app.api.composers.customer_composite import customer_composer
from app.api.dependencies import build_response, require_company_member
from app.api.shared_schemas.responses import MessageResponse
from .schemas import CustomerResponse, CustomerListResponse
from app.crud.customers import CustomerServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Customers"])


@router.get(
    "/customers/{customer_id}",
    responses={200: {"model": CustomerResponse}, 404: {"model": MessageResponse}},
)
async def get_customer_by_id(
    customer_id: str,
    company_id: str,
    customer_services: CustomerServices = Depends(customer_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    customer_in_db = await customer_services.search_by_id(
        id=customer_id, company_id=company_id
    )
    return build_response(
        status_code=200, message="Customer found with success", data=customer_in_db
    )


@router.get(
    "/customers",
    responses={200: {"model": CustomerListResponse}, 204: {"description": "No Content"}},
)
async def get_customers(
    company_id: str,
    customer_services: CustomerServices = Depends(customer_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    customers = await customer_services.search_all(company_id=company_id)
    if customers:
        return build_response(
            status_code=200, message="Customers found with success", data=customers
        )
    return Response(status_code=204)
