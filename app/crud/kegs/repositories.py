from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import KegModel
from .schemas import Keg, KegInDB

_logger = get_logger(__name__)


class KegRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, keg: Keg, company_id: str) -> KegInDB:
        try:
            json = jsonable_encoder(keg.model_dump())
            model = KegModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            model.save()
            return KegInDB.model_validate(model)
        except Exception as error:
            _logger.error(f"Error on create_keg: {str(error)}")
            raise NotFoundError(message="Error on create new keg")

    async def update(
        self, keg_id: str, company_id: str, keg: dict
    ) -> KegInDB:
        try:
            model: KegModel = KegModel.objects(
                id=keg_id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"Keg #{keg_id} not found")
            model.update(**keg)
            model.save()
            return await self.select_by_id(keg_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_keg: {str(error)}")
            raise NotFoundError(message="Error on update keg")

    async def select_by_id(self, id: str, company_id: str) -> KegInDB:
        try:
            model: KegModel = KegModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            return KegInDB.model_validate(model)
        except ValidationError:
            raise NotFoundError(message=f"Keg #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"Keg #{id} not found")

    async def select_all(self, company_id: str) -> List[KegInDB]:
        try:
            kegs: List[KegInDB] = []
            for model in KegModel.objects(company_id=company_id, is_active=True).order_by(
                "number"
            ):
                kegs.append(KegInDB.model_validate(model))
            return kegs
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Kegs not found")

    async def delete_by_id(self, id: str, company_id: str) -> KegInDB:
        try:
            model: KegModel = KegModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"Keg #{id} not found")
            model.soft_delete()
            model.save()
            return KegInDB.model_validate(model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"Keg #{id} not found")
