import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.core.exceptions import NotFoundError
from app.crud.pressure_gauges.models import PressureGaugeModel
from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.crud.pressure_gauges.schemas import (
    PressureGauge,
    PressureGaugeStatus,
    PressureGaugeType,
)


class TestPressureGaugeRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def _build_gauge(self, brand: str = "Acme") -> PressureGauge:
        return PressureGauge(
            brand=brand,
            type=PressureGaugeType.SIMPLE,
            serial_number="SN1",
            last_calibration_date=None,
            status=PressureGaugeStatus.ACTIVE,
            notes="",
        )

    def test_create_gauge(self):
        repository = PressureGaugeRepository()
        gauge = self._build_gauge()
        result = asyncio.run(repository.create(gauge, "com1"))
        self.assertEqual(result.brand, "Acme")
        self.assertEqual(PressureGaugeModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = PressureGaugeModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        repository = PressureGaugeRepository()
        res = asyncio.run(repository.select_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = PressureGaugeRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid", "com1"))

    def test_select_all(self):
        PressureGaugeModel(
            **self._build_gauge("A").model_dump(), company_id="com1"
        ).save()
        PressureGaugeModel(
            **self._build_gauge("B").model_dump(), company_id="com1"
        ).save()
        repository = PressureGaugeRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_gauge(self):
        doc = PressureGaugeModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        repository = PressureGaugeRepository()
        updated = asyncio.run(
            repository.update(doc.id, doc.company_id, {"brand": "New"})
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_gauge(self):
        doc = PressureGaugeModel(**self._build_gauge().model_dump(), company_id="com1")
        doc.save()
        repository = PressureGaugeRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(PressureGaugeModel.objects(id=doc.id).first().is_active)

    def test_delete_gauge_not_found(self):
        repository = PressureGaugeRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
