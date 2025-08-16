from fastapi import Depends

from app.api.dependencies.cache_users import get_cached_users
from app.api.dependencies.get_access_token import get_access_token
from app.crud.users.repositories import UserRepository
from app.crud.users.services import UserServices


async def user_composer(
    access_token=Depends(get_access_token),
    cached_users=Depends(get_cached_users),
) -> UserServices:
    user_repository = UserRepository(
        access_token=access_token,
        cache_users=cached_users
    )

    user_services = UserServices(
        user_repository=user_repository,
    )
    return user_services
