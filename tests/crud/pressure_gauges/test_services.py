import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.crud.pressure_gauges.services import PressureGaugeServices
from app.crud.pressure_gauges.schemas import (
    PressureGauge,
    UpdatePressureGauge,
    PressureGaugeStatus,
    PressureGaugeType,
)
from app.crud.pressure_gauges.models import PressureGaugeModel
from app.core.exceptions import NotFoundError


class TestPressureGaugeServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = PressureGaugeRepository()
        self.services = PressureGaugeServices(self.repository)

    def tearDown(self) -> None:
        disconnect()

    def _build_gauge(self, brand: str = "Acme", company_id: str = "com1") -> PressureGauge:
        return PressureGauge(
            brand=brand,
            type=PressureGaugeType.ANALOG,
            serial_number="SN1",
            last_calibration_date=None,
            status=PressureGaugeStatus.ACTIVE,
            notes="",
            company_id=company_id,
        )

    def test_create_gauge(self):
        result = asyncio.run(self.services.create(self._build_gauge()))
        self.assertEqual(result.brand, "Acme")

    def test_search_by_id(self):
        doc = PressureGaugeModel(**self._build_gauge().model_dump())
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        PressureGaugeModel(**self._build_gauge().model_dump()).save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 1)

    def test_update_gauge(self):
        doc = PressureGaugeModel(**self._build_gauge().model_dump())
        doc.save()
        updated = asyncio.run(
            self.services.update(
                doc.id, doc.company_id, UpdatePressureGauge(brand="New")
            )
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_gauge(self):
        doc = PressureGaugeModel(**self._build_gauge().model_dump())
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
