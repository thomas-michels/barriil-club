import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.beer_types.repositories import BeerTypeRepository
from app.crud.beer_types.services import BeerTypeServices
from app.crud.beer_types.schemas import BeerType, UpdateBeerType
from app.crud.beer_types.models import BeerTypeModel
from app.core.exceptions import NotFoundError


class TestBeerTypeServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = BeerTypeRepository()
        self.services = BeerTypeServices(self.repository)

    def tearDown(self) -> None:
        disconnect()

    def _build_beer_type(self, name: str = "Pale Ale", company_id: str = "com1") -> BeerType:
        return BeerType(
            name=name,
            producer="Brew Co",
            abv=5.0,
            ibu=40.0,
            description="Tasty",
            default_sale_price_per_l=10.0,
            company_id=company_id,
        )

    def test_create_beer_type(self):
        result = asyncio.run(self.services.create(self._build_beer_type()))
        self.assertEqual(result.name, "Pale Ale")

    def test_search_by_id(self):
        doc = BeerTypeModel(**self._build_beer_type().model_dump())
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        BeerTypeModel(**self._build_beer_type().model_dump()).save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 1)

    def test_update_beer_type(self):
        doc = BeerTypeModel(**self._build_beer_type().model_dump())
        doc.save()
        updated = asyncio.run(
            self.services.update(doc.id, doc.company_id, UpdateBeerType(name="New"))
        )
        self.assertEqual(updated.name, "New")

    def test_delete_beer_type(self):
        doc = BeerTypeModel(**self._build_beer_type().model_dump())
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
