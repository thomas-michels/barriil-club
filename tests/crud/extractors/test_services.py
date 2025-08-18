import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.extractors.repositories import ExtractorRepository
from app.crud.extractors.services import ExtractorServices
from app.crud.extractors.schemas import Extractor, UpdateExtractor
from app.crud.extractors.models import ExtractorModel
from app.core.exceptions import NotFoundError


class TestExtractorServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = ExtractorRepository()
        self.services = ExtractorServices(self.repository)

    def tearDown(self) -> None:
        disconnect()

    def _build_extractor(self, brand: str = "BrandX") -> Extractor:
        return Extractor(brand=brand)

    def test_create_extractor(self):
        extractor = self._build_extractor()
        result = asyncio.run(self.services.create(extractor, "com1"))
        self.assertEqual(result.brand, "BrandX")
        self.assertEqual(ExtractorModel.objects.count(), 1)

    def test_search_by_id(self):
        doc = ExtractorModel(**self._build_extractor().model_dump(), company_id="com1")
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, "com1"))
        self.assertEqual(res.id, doc.id)

    def test_search_by_id_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id("invalid", "com1"))

    def test_search_all(self):
        ExtractorModel(**self._build_extractor("A").model_dump(), company_id="com1").save()
        ExtractorModel(**self._build_extractor("B").model_dump(), company_id="com1").save()
        ExtractorModel(**self._build_extractor("C").model_dump(), company_id="com2").save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_extractor(self):
        doc = ExtractorModel(**self._build_extractor("Old").model_dump(), company_id="com1")
        doc.save()
        updated = asyncio.run(
            self.services.update(doc.id, "com1", UpdateExtractor(brand="New"))
        )
        self.assertEqual(updated.brand, "New")

    def test_update_extractor_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.update("invalid", "com1", UpdateExtractor(brand="New"))
            )

    def test_delete_extractor(self):
        doc = ExtractorModel(**self._build_extractor("Del").model_dump(), company_id="com1")
        doc.save()
        result = asyncio.run(self.services.delete_by_id(doc.id, "com1"))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(ExtractorModel.objects(id=doc.id).first().is_active)

    def test_delete_extractor_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
