from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import BeerTypeModel
from .schemas import BeerType, BeerTypeInDB

_logger = get_logger(__name__)


class BeerTypeRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, beer_type: BeerType, company_id: str) -> BeerTypeInDB:
        try:
            json = jsonable_encoder(beer_type.model_dump())
            model = BeerTypeModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            model.save()
            return BeerTypeInDB.model_validate(model)
        except Exception as error:
            _logger.error(f"Error on create_beer_type: {str(error)}")
            raise NotFoundError(message="Error on create new beer type")

    async def update(
        self, beer_type_id: str, company_id: str, beer_type: dict
    ) -> BeerTypeInDB:
        try:
            model: BeerTypeModel = BeerTypeModel.objects(
                id=beer_type_id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"BeerType #{beer_type_id} not found")
            model.update(**beer_type)
            model.save()
            return await self.select_by_id(beer_type_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_beer_type: {str(error)}")
            raise NotFoundError(message="Error on update beer type")

    async def select_by_id(self, id: str, company_id: str) -> BeerTypeInDB:
        try:
            model: BeerTypeModel = BeerTypeModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            return BeerTypeInDB.model_validate(model)
        except ValidationError:
            raise NotFoundError(message=f"BeerType #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"BeerType #{id} not found")

    async def select_all(self, company_id: str) -> List[BeerTypeInDB]:
        try:
            beer_types: List[BeerTypeInDB] = []
            for model in BeerTypeModel.objects(company_id=company_id, is_active=True).order_by(
                "name"
            ):
                beer_types.append(BeerTypeInDB.model_validate(model))
            return beer_types
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Beer types not found")

    async def delete_by_id(self, id: str, company_id: str) -> BeerTypeInDB:
        try:
            model: BeerTypeModel = BeerTypeModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"BeerType #{id} not found")
            model.soft_delete()
            model.save()
            return BeerTypeInDB.model_validate(model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"BeerType #{id} not found")
