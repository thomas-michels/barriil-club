from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import ExtractorModel
from .schemas import Extractor, ExtractorInDB

_logger = get_logger(__name__)


class ExtractorRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, extractor: Extractor, company_id: str) -> ExtractorInDB:
        try:
            json = jsonable_encoder(extractor.model_dump())
            extractor_model = ExtractorModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            extractor_model.save()
            return ExtractorInDB.model_validate(extractor_model)
        except Exception as error:
            _logger.error(f"Error on create_extractor: {str(error)}")
            raise NotFoundError(message="Error on create new extractor")

    async def update(
        self, extractor_id: str, company_id: str, extractor: dict
    ) -> ExtractorInDB:
        try:
            extractor_model: ExtractorModel = ExtractorModel.objects(
                id=extractor_id, company_id=company_id, is_active=True
            ).first()
            if not extractor_model:
                raise NotFoundError(message=f"Extractor #{extractor_id} not found")

            extractor_model.update(**extractor)
            extractor_model.save()

            return await self.select_by_id(extractor_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_extractor: {str(error)}")
            raise NotFoundError(message="Error on update extractor")

    async def select_by_id(self, id: str, company_id: str) -> ExtractorInDB:
        try:
            extractor_model: ExtractorModel = ExtractorModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            return ExtractorInDB.model_validate(extractor_model)
        except ValidationError:
            raise NotFoundError(message=f"Extractor #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"Extractor #{id} not found")

    async def select_all(self, company_id: str) -> List[ExtractorInDB]:
        try:
            extractors: List[ExtractorInDB] = []
            for extractor_model in ExtractorModel.objects(
                company_id=company_id, is_active=True
            ):
                extractors.append(ExtractorInDB.model_validate(extractor_model))
            return extractors
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Extractors not found")

    async def delete_by_id(self, id: str, company_id: str) -> ExtractorInDB:
        try:
            extractor_model: ExtractorModel = ExtractorModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not extractor_model:
                raise NotFoundError(message=f"Extractor #{id} not found")
            extractor_model.soft_delete()
            extractor_model.save()
            return ExtractorInDB.model_validate(extractor_model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"Extractor #{id} not found")
