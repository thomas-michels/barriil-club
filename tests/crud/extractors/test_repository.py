import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.extractors.repositories import ExtractorRepository
from app.crud.extractors.models import ExtractorModel
from app.crud.extractors.schemas import Extractor
from app.core.exceptions import NotFoundError


class TestExtractorRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def _build_extractor(self, brand: str = "BrandX") -> Extractor:
        return Extractor(brand=brand)

    def test_create_extractor(self):
        repository = ExtractorRepository()
        extractor = self._build_extractor()
        result = asyncio.run(repository.create(extractor, "com1"))
        self.assertEqual(result.brand, "BrandX")
        self.assertEqual(ExtractorModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = ExtractorModel(**self._build_extractor().model_dump(), company_id="com1")
        doc.save()
        repository = ExtractorRepository()
        res = asyncio.run(repository.select_by_id(doc.id, "com1"))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_wrong_company(self):
        doc = ExtractorModel(**self._build_extractor().model_dump(), company_id="com1")
        doc.save()
        repository = ExtractorRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id(doc.id, "other"))

    def test_select_all(self):
        ExtractorModel(**self._build_extractor("A").model_dump(), company_id="com1").save()
        ExtractorModel(**self._build_extractor("B").model_dump(), company_id="com1").save()
        ExtractorModel(**self._build_extractor("C").model_dump(), company_id="com2").save()
        repository = ExtractorRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_extractor(self):
        doc = ExtractorModel(**self._build_extractor("Old").model_dump(), company_id="com1")
        doc.save()
        repository = ExtractorRepository()
        updated = asyncio.run(
            repository.update(doc.id, "com1", {"brand": "New"})
        )
        self.assertEqual(updated.brand, "New")

    def test_update_extractor_not_found(self):
        repository = ExtractorRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(
                repository.update("invalid", "com1", {"brand": "New"})
            )

    def test_delete_extractor(self):
        doc = ExtractorModel(**self._build_extractor("Del").model_dump(), company_id="com1")
        doc.save()
        repository = ExtractorRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, "com1"))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(ExtractorModel.objects(id=doc.id).first().is_active)

    def test_delete_extractor_not_found(self):
        repository = ExtractorRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
