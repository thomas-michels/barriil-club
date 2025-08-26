from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import CylinderModel
from .schemas import Cylinder, CylinderInDB

_logger = get_logger(__name__)


class CylinderRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, cylinder: Cylinder, company_id: str) -> CylinderInDB:
        try:
            json = jsonable_encoder(cylinder.model_dump())
            model = CylinderModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            model.save()
            return CylinderInDB.model_validate(model)
        except Exception as error:
            _logger.error(f"Error on create_cylinder: {str(error)}")
            raise NotFoundError(message="Error on create new cylinder")

    async def update(
        self, cylinder_id: str, company_id: str, cylinder: dict
    ) -> CylinderInDB:
        try:
            model: CylinderModel = CylinderModel.objects(
                id=cylinder_id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"Cylinder #{cylinder_id} not found")
            model.update(**cylinder)
            model.save()
            return await self.select_by_id(cylinder_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_cylinder: {str(error)}")
            raise NotFoundError(message="Error on update cylinder")

    async def select_by_id(self, id: str, company_id: str) -> CylinderInDB:
        try:
            model: CylinderModel = CylinderModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            return CylinderInDB.model_validate(model)
        except ValidationError:
            raise NotFoundError(message=f"Cylinder #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"Cylinder #{id} not found")

    async def select_all(self, company_id: str) -> List[CylinderInDB]:
        try:
            cylinders: List[CylinderInDB] = []
            for model in CylinderModel.objects(
                company_id=company_id, is_active=True
            ).order_by("number"):
                cylinders.append(CylinderInDB.model_validate(model))
            return cylinders
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Cylinders not found")

    async def delete_by_id(self, id: str, company_id: str) -> CylinderInDB:
        try:
            model: CylinderModel = CylinderModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not model:
                raise NotFoundError(message=f"Cylinder #{id} not found")
            model.soft_delete()
            model.save()
            return CylinderInDB.model_validate(model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"Cylinder #{id} not found")
