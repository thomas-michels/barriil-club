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
    UpdateExtractionKit,
)
from app.crud.extraction_kits.services import ExtractionKitServices


class TestExtractionKitServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        ExtractionKitModel.drop_collection()
        self.repository = ExtractionKitRepository()
        self.services = ExtractionKitServices(self.repository)

    def tearDown(self) -> None:
        disconnect()

    def _build_gauge(
        self, brand: str = "Acme", serial_number: str = "SN1"
    ) -> ExtractionKit:
        return ExtractionKit(
            brand=brand,
            type=ExtractionKitType.SIMPLE,
            serial_number=serial_number,
            last_calibration_date=None,
            status=ExtractionKitStatus.ACTIVE,
            notes="",
        )

    def test_create_gauge(self):
        result = asyncio.run(self.services.create(self._build_gauge(), "com1"))
        self.assertEqual(result.brand, "Acme")

    def test_create_gauge_with_automatic_suffix(self):
        first = asyncio.run(
            self.services.create(self._build_gauge(serial_number="SN"), "com1")
        )
        self.assertEqual(first.serial_number, "SN")
        second = asyncio.run(
            self.services.create(self._build_gauge(serial_number="SN"), "com1")
        )
        self.assertEqual(second.serial_number, "SN1")

    def test_search_by_id(self):
        doc = ExtractionKitModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        ExtractionKitModel(**self._build_gauge().model_dump(), company_id="com1").save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 1)

    def test_update_gauge(self):
        doc = ExtractionKitModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        updated = asyncio.run(
            self.services.update(
                doc.id, doc.company_id, UpdateExtractionKit(brand="New")
            )
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_gauge(self):
        doc = ExtractionKitModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        res = asyncio.run(self.services.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_by_id_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id("invalid", "com1"))

    def test_delete_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
