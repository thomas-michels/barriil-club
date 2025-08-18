from fastapi import APIRouter, Depends, HTTPException, status

from app.api.composers.company_composite import company_composer
from app.api.dependencies import (
    build_response,
    ensure_user_without_company,
    require_company_member,
    require_company_owner,
    decode_jwt,
)
from app.api.shared_schemas.responses import MessageResponse
from .schemas import CompanyResponse, SubscriptionResponse
from app.crud.companies import (
    Company,
    UpdateCompany,
    CompanyMember,
    UpdateCompanySubscription,
)
from app.crud.companies.services import CompanyServices
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
    _: CompanyInDB = Depends(require_company_owner),
):
    company_in_db = await company_services.add_member(company_id=company_id, member=member)
    return build_response(
        status_code=200, message="Member added with success", data=company_in_db
    )


@router.delete(
    "/companies/{company_id}/members/me",
    responses={200: {"model": CompanyResponse}, 403: {"model": MessageResponse}},
)
async def leave_company(
    company_id: str,
    company_services: CompanyServices = Depends(company_composer),
    current_user: UserInDB = Depends(decode_jwt),
    company: CompanyInDB = Depends(require_company_member),
):
    if any(
        member.user_id == current_user.user_id and member.role == "owner"
        for member in company.members
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner cannot leave the company",
        )

    company_in_db = await company_services.remove_member(
        company_id=company_id, user_id=current_user.user_id
    )
    return build_response(
        status_code=200, message="Member removed with success", data=company_in_db
    )


@router.delete(
    "/companies/{company_id}/members/{user_id}",
    responses={200: {"model": CompanyResponse}, 404: {"model": MessageResponse}},
)
async def remove_member(
    company_id: str,
    user_id: str,
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_company_owner),
):
    company_in_db = await company_services.remove_member(
        company_id=company_id, user_id=user_id
    )
    return build_response(
        status_code=200, message="Member removed with success", data=company_in_db
    )


@router.put(
    "/companies/{company_id}/subscription",
    responses={200: {"model": SubscriptionResponse}, 404: {"model": MessageResponse}},
)
async def update_company_subscription(
    company_id: str,
    subscription: UpdateCompanySubscription,
    company_services: CompanyServices = Depends(company_composer),
    _: CompanyInDB = Depends(require_company_member),
):
    company_in_db = await company_services.update_subscription(
        id=company_id, subscription=subscription
    )
    return build_response(
        status_code=200,
        message="Subscription updated with success",
        data=company_in_db.subscription,
    )
