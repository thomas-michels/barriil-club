from fastapi import APIRouter, Depends

from app.api.composers.company_composite import company_composer
from app.api.dependencies import build_response, require_company_member, require_user_company
from app.api.shared_schemas.responses import MessageResponse
from app.core.exceptions import NotFoundError
from .schemas import CompanyResponse, CompanyListResponse, SubscriptionResponse
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Companies"])


@router.get(
    "/companies/{company_id}",
    responses={200: {"model": CompanyResponse}, 404: {"model": MessageResponse}},
)
async def get_company_by_id(
    company_id: str,
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    company_in_db = await company_services.search_by_id(id=company_id)
    return build_response(
        status_code=200, message="Company found with success", data=company_in_db
    )


@router.get(
    "/companies/{company_id}/subscription",
    responses={200: {"model": SubscriptionResponse}, 404: {"model": MessageResponse}},
)
async def get_company_subscription(
    company_id: str,
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    subscription = await company_services.get_subscription(id=company_id)
    return build_response(
        status_code=200,
        message="Subscription found with success",
        data=subscription,
    )


@router.get(
    "/companies",
    responses={200: {"model": CompanyListResponse}},
)
async def get_companies(
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_user_company),
):
    try:
        companies = await company_services.search_all()
    except NotFoundError:
        companies = []
    return build_response(
        status_code=200, message="Companies found with success", data=companies
    )
