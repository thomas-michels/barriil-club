import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.core.exceptions import NotFoundError
from app.crud.extraction_kits.models import ExtractionKitModel
from app.crud.extraction_kits.repositories import ExtractionKitRepository
from app.crud.extraction_kits.schemas import (
    ExtractionKit,
    ExtractionKitStatus,
    ExtractionKitType,
)


class TestExtractionKitRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def _build_gauge(self, brand: str = "Acme") -> ExtractionKit:
        return ExtractionKit(
            brand=brand,
            type=ExtractionKitType.SIMPLE,
            serial_number="SN1",
            last_calibration_date=None,
            status=ExtractionKitStatus.ACTIVE,
            notes="",
        )

    def test_create_gauge(self):
        repository = ExtractionKitRepository()
        gauge = self._build_gauge()
        result = asyncio.run(repository.create(gauge, "com1"))
        self.assertEqual(result.brand, "Acme")
        self.assertEqual(ExtractionKitModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = ExtractionKitModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        repository = ExtractionKitRepository()
        res = asyncio.run(repository.select_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = ExtractionKitRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid", "com1"))

    def test_select_all(self):
        ExtractionKitModel(
            **self._build_gauge("A").model_dump(), company_id="com1"
        ).save()
        ExtractionKitModel(
            **self._build_gauge("B").model_dump(), company_id="com1"
        ).save()
        repository = ExtractionKitRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_gauge(self):
        doc = ExtractionKitModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        repository = ExtractionKitRepository()
        updated = asyncio.run(
            repository.update(doc.id, doc.company_id, {"brand": "New"})
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_gauge(self):
        doc = ExtractionKitModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        repository = ExtractionKitRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(ExtractionKitModel.objects(id=doc.id).first().is_active)

    def test_delete_gauge_not_found(self):
        repository = ExtractionKitRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
