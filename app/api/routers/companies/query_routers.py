from fastapi import APIRouter, Depends, Response

from app.api.composers.company_composite import company_composer
from app.api.dependencies import build_response
from app.api.shared_schemas.responses import MessageResponse
from .schemas import CompanyResponse, CompanyListResponse
from app.crud.companies import CompanyServices

router = APIRouter(tags=["Companies"])


@router.get(
    "/companies/{company_id}",
    responses={200: {"model": CompanyResponse}, 404: {"model": MessageResponse}},
)
async def get_company_by_id(
    company_id: str,
    company_services: CompanyServices = Depends(company_composer),
):
    company_in_db = await company_services.search_by_id(id=company_id)
    return build_response(
        status_code=200, message="Company found with success", data=company_in_db
    )


@router.get(
    "/companies",
    responses={200: {"model": CompanyListResponse}, 204: {"description": "No Content"}},
)
async def get_companies(
    company_services: CompanyServices = Depends(company_composer),
):
    companies = await company_services.search_all()
    if companies:
        return build_response(
            status_code=200, message="Companies found with success", data=companies
        )
    return Response(status_code=204)
