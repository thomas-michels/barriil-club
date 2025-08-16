from typing import Dict

from app.api.shared_schemas.terms_of_use import FilterTermOfUse
from app.api.shared_schemas.token import TokenData
from app.core.configs import get_logger
from app.crud.users.repositories import UserRepository
from app.crud.users.schemas import UserInDB

logger = get_logger(__name__)


class AuthenticationServices:
    def __init__(
            self,
            user_repository: UserRepository,
        ) -> None:
        self.__user_repository = user_repository

    async def get_current_user(self, token: TokenData) -> UserInDB:
        user_in_db = await self.__user_repository.select_by_id(id=token.id)
        return user_in_db
