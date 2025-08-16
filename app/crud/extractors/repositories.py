from typing import List

from app.core.exceptions import NotFoundError

from .models import ExtractorModel
from .schemas import Extractor, ExtractorInDB, UpdateExtractor


class ExtractorRepository:
    async def create(self, extractor: Extractor) -> ExtractorInDB:
        document = ExtractorModel(**extractor.model_dump())
        document.save()
        return ExtractorInDB.model_validate(document)

    async def select_by_id(self, id: str, raise_404: bool = True) -> ExtractorInDB | None:
        document = ExtractorModel.objects(id=id, is_active=True).first()
        if document:
            return ExtractorInDB.model_validate(document)
        if raise_404:
            raise NotFoundError(message=f"Extractor {id} not found")
        return None

    async def select_all(self) -> List[ExtractorInDB]:
        documents = ExtractorModel.objects(is_active=True).all()
        return [ExtractorInDB.model_validate(doc) for doc in documents]

    async def update(self, id: str, extractor: UpdateExtractor) -> ExtractorInDB:
        document = ExtractorModel.objects(id=id, is_active=True).first()
        if not document:
            raise NotFoundError(message=f"Extractor {id} not found")
        data = extractor.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in data.items():
            setattr(document, field, value)
        document.base_update()
        document.save()
        return ExtractorInDB.model_validate(document)

    async def delete_by_id(self, id: str) -> bool:
        document = ExtractorModel.objects(id=id, is_active=True).first()
        if not document:
            return False
        document.soft_delete()
        document.save()
        return True
