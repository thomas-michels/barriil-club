from fastapi import APIRouter, Depends, Security, Response

from app.api.composers.user_composite import user_composer
from app.api.composers.company_composite import company_composer
from app.api.dependencies import build_response, decode_jwt
from app.api.shared_schemas.responses import MessageResponse
from .schemas import (
    GetCurrentUserResponse,
    GetUserByIdResponse,
    GetUserByEmailResponse,
    GetUsersResponse,
    CurrentUserWithCompany,
)
from app.crud.users import UserInDB, UserServices
from app.crud.companies import CompanyServices

router = APIRouter(tags=["Users"])


@router.get(
    "/users/me/",
    responses={200: {"model": GetCurrentUserResponse}},
)
async def current_user(
    current_user: UserInDB = Security(decode_jwt, scopes=["user:me"]),
    company_services: CompanyServices = Depends(company_composer),
):
    company = await company_services.search_by_user(user_id=current_user.user_id)
    data = CurrentUserWithCompany(user_id=current_user.user_id, company=company)
    return build_response(
        status_code=200,
        message="User found with success",
        data=data,
    )


@router.get(
    "/users/{user_id}",
    responses={
        200: {"model": GetUserByIdResponse},
        404: {"model": MessageResponse},
    },
)
async def get_user_by_id(
    user_id: str,
    current_user: UserInDB = Security(decode_jwt, scopes=["user:get"]),
    user_services: UserServices = Depends(user_composer),
):
    user_in_db = await user_services.search_by_id(id=user_id)

    if user_in_db:
        return build_response(
            status_code=200, message="User found with success", data=user_in_db
        )

    else:
        return build_response(
            status_code=404, message=f"User {user_id} not found", data=None
        )


@router.get(
    "/users/email/{email}",
    responses={
        200: {"model": GetUserByEmailResponse},
        404: {"model": MessageResponse},
    },
)
async def get_user_by_email(
    email: str,
    current_user: UserInDB = Security(decode_jwt, scopes=["user:get"]),
    user_services: UserServices = Depends(user_composer),
):
    user_in_db = await user_services.search_by_email(email=email)

    if user_in_db:
        return build_response(
            status_code=200, message="User found with success", data=user_in_db
        )

    else:
        return build_response(
            status_code=404,
            message=f"User with email {email} not found",
            data=None,
        )


@router.get(
    "/users",
    responses={
        200: {"model": GetUsersResponse},
        204: {"description": "No Content"},
    },
)
async def get_users(
    current_user: UserInDB = Security(decode_jwt, scopes=["user:get"]),
    user_services: UserServices = Depends(user_composer),
):
    users = await user_services.search_all()

    if users:
        return build_response(
            status_code=200, message="Users found with success", data=users
        )

    else:
        return Response(status_code=204)
