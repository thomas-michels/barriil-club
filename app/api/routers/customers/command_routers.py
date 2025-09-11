from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.customer_composite import customer_composer
from app.api.dependencies import build_response, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from .schemas import CustomerResponse
from app.crud.customers import Customer, UpdateCustomer, CustomerServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Customers"])


@router.post(
    "/customers",
    responses={201: {"model": CustomerResponse}, 400: {"model": MessageResponse}},
)
async def create_customer(
    customer: Customer,
    company: CompanyInDB = Depends(require_user_company),
    customer_services: CustomerServices = Depends(customer_composer),
):
    customer_in_db = await customer_services.create(
        customer=customer, company_id=str(company.id)
    )
    if not customer_in_db:
        raise HTTPException(status_code=400, detail="Cliente não criado")
    return build_response(
        status_code=201, message="Customer created with success", data=customer_in_db
    )


@router.put(
    "/customers/{customer_id}",
    responses={200: {"model": CustomerResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def update_customer(
    customer_id: str,
    customer: UpdateCustomer,
    customer_services: CustomerServices = Depends(customer_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    customer_in_db = await customer_services.update(
        id=customer_id, company_id=str(company.id), customer=customer
    )
    if not customer_in_db:
        raise HTTPException(status_code=400, detail="Cliente não atualizado")
    return build_response(
        status_code=200, message="Customer updated with success", data=customer_in_db
    )


@router.delete(
    "/customers/{customer_id}",
    responses={200: {"model": CustomerResponse}, 400: {"model": MessageResponse}, 404: {"model": MessageResponse}},
)
async def delete_customer(
    customer_id: str,
    customer_services: CustomerServices = Depends(customer_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    customer_in_db = await customer_services.delete_by_id(
        id=customer_id, company_id=str(company.id)
    )
    if not customer_in_db:
        raise HTTPException(status_code=400, detail="Cliente não excluído")
    return build_response(
        status_code=200, message="Customer deleted with success", data=customer_in_db
    )
