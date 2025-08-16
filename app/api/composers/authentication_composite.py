from fastapi import Depends

from app.api.dependencies.cache_users import get_cached_users
from app.api.dependencies.get_access_token import get_access_token
from app.crud.authetication.services import AuthenticationServices
from app.crud.users.repositories import UserRepository


async def authentication_composer(
    access_token=Depends(get_access_token),
    cached_users=Depends(get_cached_users),
) -> AuthenticationServices:
    user_repository = UserRepository(
        access_token=access_token,
        cache_users=cached_users
    )

    authentication_services = AuthenticationServices(
        user_repository=user_repository,
    )
    return authentication_services
