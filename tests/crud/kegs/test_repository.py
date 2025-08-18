import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.models import KegModel
from app.crud.kegs.schemas import Keg, KegStatus
from app.crud.beer_types.models import BeerTypeModel
from app.core.exceptions import NotFoundError


class TestKegRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        # create beer type for reference
        self.beer_type = BeerTypeModel(
            name="Pale Ale",
            default_sale_price_per_l=10.0,
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
        repository = KegRepository()
        keg = self._build_keg()
        result = asyncio.run(repository.create(keg, "com1"))
        self.assertEqual(result.number, "1")
        self.assertEqual(KegModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = KegModel(**self._build_keg().model_dump(), company_id="com1")
        doc.save()
        repository = KegRepository()
        res = asyncio.run(repository.select_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = KegRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid", "com1"))

    def test_select_all(self):
        KegModel(**self._build_keg("1").model_dump(), company_id="com1").save()
        KegModel(**self._build_keg("2").model_dump(), company_id="com1").save()
        repository = KegRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_keg(self):
        doc = KegModel(**self._build_keg().model_dump(), company_id="com1")
        doc.save()
        repository = KegRepository()
        updated = asyncio.run(
            repository.update(doc.id, doc.company_id, {"number": "3"})
        )
        self.assertEqual(updated.number, "3")

    def test_delete_keg(self):
        doc = KegModel(**self._build_keg().model_dump(), company_id="com1")
        doc.save()
        repository = KegRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(KegModel.objects(id=doc.id).first().is_active)

    def test_delete_keg_not_found(self):
        repository = KegRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
