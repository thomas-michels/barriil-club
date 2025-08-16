from fastapi import APIRouter, Depends, Security

from app.api.composers.user_composite import user_composer
from app.api.dependencies import build_response, decode_jwt
from app.api.shared_schemas.responses import MessageResponse
from .schemas import (
    DeleteCurrentUserResponse,
    DeleteUserResponse,
    UpdateCurrentUserResponse,
    UpdateUserResponse,
)
from app.crud.users import (
    UpdateUser,
    UserInDB,
    UserServices,
)

router = APIRouter(tags=["Users"])


# @router.post("/users", responses={201: {"model": UserInDB}})
# async def create_user(
#     user: User,
#     user_services: UserServices = Depends(user_composer),
# ):
#     user_in_db = await user_services.create(
#         user=user
#     )

#     if user_in_db:
#         return build_response(
#             status_code=201, message="User created with success", data=user_in_db
#         )

#     else:
#         return build_response(
#             status_code=400, message="Some error happened on create a user", data=None
#         )


@router.put(
    "/users/me",
    responses={
        200: {"model": UpdateCurrentUserResponse},
        400: {"model": MessageResponse},
    },
)
async def update_user(
    user: UpdateUser,
    current_user: UserInDB = Security(decode_jwt, scopes=["user:me"]),
    user_services: UserServices = Depends(user_composer),
):
    user_in_db = await user_services.update(id=current_user.user_id, updated_user=user)

    if user_in_db:
        return build_response(
            status_code=200, message="User updated with success", data=user_in_db
        )

    else:
        return build_response(
            status_code=400, message="Some error happened on update a user", data=None
        )


@router.put(
    "/users/{user_id}",
    responses={
        200: {"model": UpdateUserResponse},
        400: {"model": MessageResponse},
    },
)
async def update_user(
    user_id: str,
    user: UpdateUser,
    current_user: UserInDB = Security(decode_jwt, scopes=["user:create"]),
    user_services: UserServices = Depends(user_composer),
):
    user_in_db = await user_services.update(id=user_id, updated_user=user)

    if user_in_db:
        return build_response(
            status_code=200, message="User updated with success", data=user_in_db
        )

    else:
        return build_response(
            status_code=400, message="Some error happened on update a user", data=None
        )


@router.delete(
    "/users/{user_id}",
    responses={
        200: {"model": DeleteUserResponse},
        404: {"model": MessageResponse},
    },
)
async def delete_user(
    user_id: str,
    current_user: UserInDB = Security(decode_jwt, scopes=["user:delete"]),
    user_services: UserServices = Depends(user_composer),
):
    user_in_db = await user_services.delete_by_id(id=user_id)

    if user_in_db:
        return build_response(
            status_code=200, message="User deleted with success", data=user_in_db
        )

    else:
        return build_response(
            status_code=404, message=f"User {user_id} not found", data=None
        )


@router.delete(
    "/users/me",
    responses={
        200: {"model": DeleteCurrentUserResponse},
        404: {"model": MessageResponse},
    },
)
async def delete_user(
    current_user: UserInDB = Security(decode_jwt, scopes=["user:me"]),
    user_services: UserServices = Depends(user_composer),
):
    user_in_db = await user_services.delete_by_id(id=current_user.user_id)

    if user_in_db:
        return build_response(
            status_code=200, message="User deleted with success", data=user_in_db
        )

    else:
        return build_response(
            status_code=404, message=f"User {current_user.id} not found", data=None
        )
