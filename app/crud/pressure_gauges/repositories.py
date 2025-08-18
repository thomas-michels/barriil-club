from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import PressureGaugeModel
from .schemas import PressureGauge, PressureGaugeInDB

_logger = get_logger(__name__)


class PressureGaugeRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, gauge: PressureGauge, company_id: str) -> PressureGaugeInDB:
        try:
            json = jsonable_encoder(gauge.model_dump())
            model = PressureGaugeModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            model.save()
            return PressureGaugeInDB.model_validate(model)
        except Exception as error:
            _logger.error(f"Error on create_gauge: {str(error)}")
            raise NotFoundError(message="Error on create new pressure gauge")

    async def update(
        self, gauge_id: str, company_id: str, gauge: dict
    ) -> PressureGaugeInDB:
        try:
            model: PressureGaugeModel = PressureGaugeModel.objects(
                id=gauge_id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"PressureGauge #{gauge_id} not found")
            model.update(**gauge)
            model.save()
            return await self.select_by_id(gauge_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_gauge: {str(error)}")
            raise NotFoundError(message="Error on update pressure gauge")

    async def select_by_id(self, id: str, company_id: str) -> PressureGaugeInDB:
        try:
            model: PressureGaugeModel = PressureGaugeModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            return PressureGaugeInDB.model_validate(model)
        except ValidationError:
            raise NotFoundError(message=f"PressureGauge #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"PressureGauge #{id} not found")

    async def select_all(self, company_id: str) -> List[PressureGaugeInDB]:
        try:
            gauges: List[PressureGaugeInDB] = []
            for model in PressureGaugeModel.objects(
                company_id=company_id, is_active=True
            ).order_by("brand"):
                gauges.append(PressureGaugeInDB.model_validate(model))
            return gauges
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Pressure gauges not found")

    async def delete_by_id(self, id: str, company_id: str) -> PressureGaugeInDB:
        try:
            model: PressureGaugeModel = PressureGaugeModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"PressureGauge #{id} not found")
            model.soft_delete()
            model.save()
            return PressureGaugeInDB.model_validate(model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"PressureGauge #{id} not found")
