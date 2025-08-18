import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.beer_dispensers.models import BeerDispenserModel
from app.crud.beer_dispensers.schemas import BeerDispenser, DispenserStatus, Voltage
from app.core.exceptions import NotFoundError


class TestBeerDispenserRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def _build_dispenser(self, brand: str = "Acme") -> BeerDispenser:
        return BeerDispenser(
            brand=brand,
            model="X1",
            serial_number="SN1",
            taps_count=4,
            voltage=Voltage.V110,
            status=DispenserStatus.ACTIVE,
            notes="",
        )

    def test_create_dispenser(self):
        repository = BeerDispenserRepository()
        dispenser = self._build_dispenser()
        result = asyncio.run(repository.create(dispenser, "com1"))
        self.assertEqual(result.brand, "Acme")
        self.assertEqual(BeerDispenserModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = BeerDispenserModel(**self._build_dispenser().model_dump(), company_id="com1")
        doc.save()
        repository = BeerDispenserRepository()
        res = asyncio.run(repository.select_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = BeerDispenserRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid", "com1"))

    def test_select_all(self):
        BeerDispenserModel(**self._build_dispenser("A").model_dump(), company_id="com1").save()
        BeerDispenserModel(**self._build_dispenser("B").model_dump(), company_id="com1").save()
        repository = BeerDispenserRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_dispenser(self):
        doc = BeerDispenserModel(**self._build_dispenser().model_dump(), company_id="com1")
        doc.save()
        repository = BeerDispenserRepository()
        updated = asyncio.run(
            repository.update(doc.id, doc.company_id, {"brand": "New"})
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_dispenser(self):
        doc = BeerDispenserModel(**self._build_dispenser().model_dump(), company_id="com1")
        doc.save()
        repository = BeerDispenserRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(BeerDispenserModel.objects(id=doc.id).first().is_active)

    def test_delete_dispenser_not_found(self):
        repository = BeerDispenserRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
