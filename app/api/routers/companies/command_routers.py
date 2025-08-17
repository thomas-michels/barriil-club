from fastapi import APIRouter, Depends

from app.api.composers.company_composite import company_composer
from app.api.dependencies import (
    build_response,
    ensure_user_without_company,
    require_company_member,
)
from app.api.shared_schemas.responses import MessageResponse
from .schemas import CompanyResponse
from app.crud.companies import Company, UpdateCompany, CompanyServices, CompanyMember
from app.crud.users.schemas import UserInDB
from app.crud.companies.schemas import CompanyInDB

router = APIRouter(tags=["Companies"])


@router.post(
    "/companies",
    responses={201: {"model": CompanyResponse}},
)
async def create_company(
    company: Company,
    user: UserInDB = Depends(ensure_user_without_company),
    company_services: CompanyServices = Depends(company_composer),
):
    company.members = [
        member for member in company.members if member.user_id != user.user_id
    ]
    company.members.append(CompanyMember(user_id=user.user_id, role="owner"))
    company_in_db = await company_services.create(company=company)
    return build_response(
        status_code=201, message="Company created with success", data=company_in_db
    )


@router.put(
    "/companies/{company_id}",
    responses={200: {"model": CompanyResponse}, 404: {"model": MessageResponse}},
)
async def update_company(
    company_id: str,
    company: UpdateCompany,
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    company_in_db = await company_services.update(id=company_id, company=company)
    return build_response(
        status_code=200, message="Company updated with success", data=company_in_db
    )


@router.delete(
    "/companies/{company_id}",
    responses={200: {"model": CompanyResponse}, 404: {"model": MessageResponse}},
)
async def delete_company(
    company_id: str,
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    company_in_db = await company_services.delete_by_id(id=company_id)
    return build_response(
        status_code=200, message="Company deleted with success", data=company_in_db
    )


@router.post(
    "/companies/{company_id}/members",
    responses={200: {"model": CompanyResponse}, 404: {"model": MessageResponse}},
)
async def add_member(
    company_id: str,
    member: CompanyMember,
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    company_in_db = await company_services.add_member(company_id=company_id, member=member)
    return build_response(
        status_code=200, message="Member added with success", data=company_in_db
    )
