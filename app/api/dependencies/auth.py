
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from jose import JWTError
from pydantic import ValidationError

from app.api.composers.authentication_composite import authentication_composer
from app.api.dependencies.verify_token import ValidateToken
from app.api.shared_schemas.token import TokenData
from app.core.exceptions.users import NotFoundError
from app.crud.authetication import AuthenticationServices
from app.crud.users.schemas import UserInDB


async def decode_jwt(
    request: Request,
    security_scopes: SecurityScopes,
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    authetication_services: AuthenticationServices = Depends(authentication_composer),
) -> UserInDB:
    try:
        auth: ValidateToken = request.app.state.auth

        auth_result = await auth.verify(
            scopes=security_scopes,
            token=token.credentials
        )

        token_scopes = auth_result.get("scopes", [])

        token_data = TokenData(scopes=token_scopes, id=auth_result["sub"])

        current_user = await authetication_services.get_current_user(token=token_data)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not security_scopes.scopes:
            return current_user

        # verify_scopes(
        #     scopes_needed=security_scopes,
        #     user_role=current_user.organizations_roles[organization_id].role,
        #     current_user=current_user
        # )

        return current_user

    except (JWTError, ValidationError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# def verify_scopes(
#     scopes_needed: SecurityScopes | list, user_role: RoleEnum, current_user: CompleteUserInDB
# ) -> bool:
#     user_scopes = get_role_permissions(role=user_role)

#     scopes = []

#     if isinstance(scopes_needed, SecurityScopes):
#         scopes = scopes_needed.scopes

#     else:
#         scopes = scopes_needed

#     if not scopes:
#         return True

#     for scope in scopes:
#         if scope in user_scopes:
#             return True

#         # Only super users can use that
#         if scope in ["user:get"]:
#             if current_user.app_metadata and current_user.app_metadata.get("superuser", False):
#                 return True

#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Access denied",
#         headers={"WWW-Authenticate": "Bearer"},
#     )


# def verify_super_user(current_user: CompleteUserInDB):
#     # if current_user.app_metadata and current_user.app_metadata.get("superuser", False):
#     if current_user.app_metadata:
#         return True

#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Access denied",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
