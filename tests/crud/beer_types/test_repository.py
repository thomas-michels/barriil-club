import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.beer_types.repositories import BeerTypeRepository
from app.crud.beer_types.models import BeerTypeModel
from app.crud.beer_types.schemas import BeerType
from app.core.exceptions import NotFoundError


class TestBeerTypeRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def _build_beer_type(self, name: str = "Pale Ale") -> BeerType:
        return BeerType(
            name=name,
            producer="Brew Co",
            abv=5.0,
            ibu=40.0,
            description="Tasty",
        )

    def test_create_beer_type(self):
        repository = BeerTypeRepository()
        beer_type = self._build_beer_type()
        result = asyncio.run(repository.create(beer_type, company_id="com1"))
        self.assertEqual(result.name, "Pale Ale")
        self.assertEqual(BeerTypeModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = BeerTypeModel(**self._build_beer_type().model_dump(), company_id="com1")
        doc.save()
        repository = BeerTypeRepository()
        res = asyncio.run(repository.select_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = BeerTypeRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid", "com1"))

    def test_select_all(self):
        BeerTypeModel(**self._build_beer_type("A").model_dump(), company_id="com1").save()
        BeerTypeModel(**self._build_beer_type("B").model_dump(), company_id="com1").save()
        repository = BeerTypeRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_beer_type(self):
        doc = BeerTypeModel(**self._build_beer_type().model_dump(), company_id="com1")
        doc.save()
        repository = BeerTypeRepository()
        updated = asyncio.run(
            repository.update(doc.id, doc.company_id, {"name": "New"})
        )
        self.assertEqual(updated.name, "New")

    def test_delete_beer_type(self):
        doc = BeerTypeModel(**self._build_beer_type().model_dump(), company_id="com1")
        doc.save()
        repository = BeerTypeRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(BeerTypeModel.objects(id=doc.id).first().is_active)

    def test_delete_beer_type_not_found(self):
        repository = BeerTypeRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
