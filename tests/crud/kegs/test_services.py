import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.services import KegServices
from app.crud.kegs.schemas import Keg, UpdateKeg, KegStatus
from app.crud.kegs.models import KegModel
from app.crud.beer_types.models import BeerTypeModel
from app.core.exceptions import NotFoundError


class TestKegServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = KegRepository()
        self.services = KegServices(self.repository)
        self.beer_type = BeerTypeModel(
            name="Pale Ale",
            company_id="com1",
        )
        self.beer_type.save()

    def tearDown(self) -> None:
        disconnect()

    def _build_keg(self, number: str = "1") -> Keg:
        return Keg(
            number=number,
            size_l=50,
            beer_type_id=str(self.beer_type.id),
            cost_price_per_l=5.0,
            sale_price_per_l=8.0,
            lot="L1",
            expiration_date=None,
            current_volume_l=25.0,
            status=KegStatus.AVAILABLE,
            notes="",
        )

    def test_create_keg(self):
        result = asyncio.run(self.services.create(self._build_keg(), "com1"))
        self.assertEqual(result.number, "1")

    def test_create_keg_allows_duplicate_number(self):
        first = asyncio.run(self.services.create(self._build_keg("10"), "com1"))
        second = asyncio.run(self.services.create(self._build_keg("10"), "com1"))
        self.assertEqual(first.number, "10")
        self.assertEqual(second.number, "10")
        self.assertNotEqual(first.id, second.id)

    def test_search_by_id(self):
        doc = KegModel(**self._build_keg().model_dump(), company_id="com1")
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        KegModel(**self._build_keg().model_dump(), company_id="com1").save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 1)

    def test_search_all_filtered_by_status(self):
        keg1 = self._build_keg("1")
        KegModel(**keg1.model_dump(), company_id="com1").save()
        keg2 = self._build_keg("2")
        keg2.status = KegStatus.IN_USE
        KegModel(**keg2.model_dump(), company_id="com1").save()
        res = asyncio.run(
            self.services.search_all("com1", status=KegStatus.AVAILABLE)
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].status, KegStatus.AVAILABLE)

    def test_update_keg(self):
        doc = KegModel(**self._build_keg().model_dump(), company_id="com1")
        doc.save()
        updated = asyncio.run(
            self.services.update(doc.id, doc.company_id, UpdateKeg(number="2"))
        )
        self.assertEqual(updated.number, "2")

    def test_delete_keg(self):
        doc = KegModel(**self._build_keg().model_dump(), company_id="com1")
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
