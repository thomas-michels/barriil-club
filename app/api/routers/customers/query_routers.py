from fastapi import APIRouter, Depends

from app.api.composers.customer_composite import customer_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from app.core.exceptions import NotFoundError
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
    customer_services: CustomerServices = Depends(customer_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    customer_in_db = await customer_services.search_by_id(
        id=customer_id, company_id=str(company.id)
    )
    return build_response(
        status_code=200, message="Customer found with success", data=customer_in_db
    )


@router.get(
    "/customers",
    responses={200: {"model": CustomerListResponse}},
)
async def get_customers(
    customer_services: CustomerServices = Depends(customer_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    try:
        customers = await customer_services.search_all(company_id=str(company.id))
    except NotFoundError:
        customers = []
    return build_response(
        status_code=200,
        message="Customers found with success",
        data=customers,
    )
