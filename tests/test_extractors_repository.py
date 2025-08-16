import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.extractors.repositories import ExtractorRepository
from app.crud.extractors.models import ExtractorModel
from app.crud.extractors.schemas import Extractor, UpdateExtractor
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

    def _build_extractor(self, brand: str = "BrandX", company_id: str = "com1") -> Extractor:
        return Extractor(brand=brand, company_id=company_id)

    def test_create_extractor(self):
        repository = ExtractorRepository()
        extractor = self._build_extractor()
        result = asyncio.run(repository.create(extractor))
        self.assertEqual(result.brand, "BrandX")
        self.assertEqual(ExtractorModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = ExtractorModel(**self._build_extractor().model_dump())
        doc.save()
        repository = ExtractorRepository()
        res = asyncio.run(repository.select_by_id(doc.id, "com1"))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_wrong_company(self):
        doc = ExtractorModel(**self._build_extractor().model_dump())
        doc.save()
        repository = ExtractorRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id(doc.id, "other"))

    def test_select_all(self):
        ExtractorModel(**self._build_extractor("A", "com1").model_dump()).save()
        ExtractorModel(**self._build_extractor("B", "com1").model_dump()).save()
        ExtractorModel(**self._build_extractor("C", "com2").model_dump()).save()
        repository = ExtractorRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_extractor(self):
        doc = ExtractorModel(**self._build_extractor("Old", "com1").model_dump())
        doc.save()
        repository = ExtractorRepository()
        updated = asyncio.run(
            repository.update(doc.id, "com1", UpdateExtractor(brand="New"))
        )
        self.assertEqual(updated.brand, "New")

    def test_update_extractor_not_found(self):
        repository = ExtractorRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(
                repository.update("invalid", "com1", UpdateExtractor(brand="New"))
            )

    def test_delete_extractor(self):
        doc = ExtractorModel(**self._build_extractor("Del", "com1").model_dump())
        doc.save()
        repository = ExtractorRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, "com1"))
        self.assertTrue(result)
        self.assertFalse(ExtractorModel.objects(id=doc.id).first().is_active)

    def test_delete_extractor_not_found(self):
        repository = ExtractorRepository()
        self.assertFalse(asyncio.run(repository.delete_by_id("invalid", "com1")))


if __name__ == "__main__":
    unittest.main()
