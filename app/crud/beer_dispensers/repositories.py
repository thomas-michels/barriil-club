from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import BeerDispenserModel
from .schemas import BeerDispenser, BeerDispenserInDB

_logger = get_logger(__name__)


class BeerDispenserRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, dispenser: BeerDispenser, company_id: str) -> BeerDispenserInDB:
        try:
            json = jsonable_encoder(dispenser.model_dump())
            model = BeerDispenserModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            model.save()
            return BeerDispenserInDB.model_validate(model)
        except Exception as error:
            _logger.error(f"Error on create_dispenser: {str(error)}")
            raise NotFoundError(message="Error on create new beer dispenser")

    async def update(
        self, dispenser_id: str, company_id: str, dispenser: dict
    ) -> BeerDispenserInDB:
        try:
            model: BeerDispenserModel = BeerDispenserModel.objects(
                id=dispenser_id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"BeerDispenser #{dispenser_id} not found")
            model.update(**dispenser)
            model.save()
            return await self.select_by_id(dispenser_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_dispenser: {str(error)}")
            raise NotFoundError(message="Error on update beer dispenser")

    async def select_by_id(
        self, id: str, company_id: str
    ) -> BeerDispenserInDB:
        try:
            model: BeerDispenserModel = BeerDispenserModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            return BeerDispenserInDB.model_validate(model)
        except ValidationError:
            raise NotFoundError(message=f"BeerDispenser #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"BeerDispenser #{id} not found")

    async def select_all(self, company_id: str) -> List[BeerDispenserInDB]:
        try:
            dispensers: List[BeerDispenserInDB] = []
            for model in BeerDispenserModel.objects(
                company_id=company_id, is_active=True
            ).order_by("brand"):
                dispensers.append(BeerDispenserInDB.model_validate(model))
            return dispensers
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Beer dispensers not found")

    async def delete_by_id(self, id: str, company_id: str) -> BeerDispenserInDB:
        try:
            model: BeerDispenserModel = BeerDispenserModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"BeerDispenser #{id} not found")
            model.soft_delete()
            model.save()
            return BeerDispenserInDB.model_validate(model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"BeerDispenser #{id} not found")
