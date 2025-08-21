import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.beer_dispensers.services import BeerDispenserServices
from app.crud.beer_dispensers.schemas import (
    BeerDispenser,
    UpdateBeerDispenser,
    DispenserStatus,
    Voltage,
)
from app.crud.beer_dispensers.models import BeerDispenserModel
from app.core.exceptions import NotFoundError


class TestBeerDispenserServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = BeerDispenserRepository()
        self.services = BeerDispenserServices(self.repository)

    def tearDown(self) -> None:
        disconnect()

    def _build_dispenser(
        self, brand: str = "Acme", serial_number: str = "SN1"
    ) -> BeerDispenser:
        return BeerDispenser(
            brand=brand,
            model="X1",
            serial_number=serial_number,
            taps_count=4,
            voltage=Voltage.V110,
            status=DispenserStatus.ACTIVE,
            notes="",
        )

    def test_create_dispenser(self):
        result = asyncio.run(self.services.create(self._build_dispenser(), "com1"))
        self.assertEqual(result.brand, "Acme")

    def test_create_dispenser_with_automatic_suffix(self):
        first = asyncio.run(
            self.services.create(self._build_dispenser(serial_number="SN"), "com1")
        )
        self.assertEqual(first.serial_number, "SN")
        second = asyncio.run(
            self.services.create(self._build_dispenser(serial_number="SN"), "com1")
        )
        self.assertEqual(second.serial_number, "SN1")

    def test_search_by_id(self):
        doc = BeerDispenserModel(**self._build_dispenser().model_dump(), company_id="com1")
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        BeerDispenserModel(**self._build_dispenser().model_dump(), company_id="com1").save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 1)

    def test_update_dispenser(self):
        doc = BeerDispenserModel(**self._build_dispenser().model_dump(), company_id="com1")
        doc.save()
        updated = asyncio.run(
            self.services.update(
                doc.id, doc.company_id, UpdateBeerDispenser(brand="New")
            )
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_dispenser(self):
        doc = BeerDispenserModel(**self._build_dispenser().model_dump(), company_id="com1")
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
