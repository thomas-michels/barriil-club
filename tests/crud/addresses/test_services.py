import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.services import AddressServices
from app.crud.addresses.schemas import Address, UpdateAddress
from app.crud.addresses.models import AddressModel
from app.core.exceptions import NotFoundError


class TestAddressServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = AddressRepository()
        self.services = AddressServices(self.repository)

    def tearDown(self) -> None:
        disconnect()

    def _build_address(self, postal_code: str = "12345") -> Address:
        return Address(
            postal_code=postal_code,
            street="Main",
            number="1",
            complement="Apt",
            district="Center",
            city="City",
            state="ST",
            reference="Near",
        )

    def test_create_address(self):
        address = self._build_address()
        result = asyncio.run(self.services.create(address))
        self.assertEqual(result.postal_code, "12345")

    def test_search_by_id(self):
        doc = AddressModel(**self._build_address().model_dump())
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        AddressModel(**self._build_address("1").model_dump()).save()
        res = asyncio.run(self.services.search_all())
        self.assertEqual(len(res), 1)

    def test_update_address(self):
        doc = AddressModel(**self._build_address().model_dump())
        doc.save()
        updated = asyncio.run(
            self.services.update(doc.id, UpdateAddress(city="New City"))
        )
        self.assertEqual(updated.city, "New City")

    def test_delete_address(self):
        doc = AddressModel(**self._build_address().model_dump())
        doc.save()
        res = asyncio.run(self.services.delete_by_id(doc.id))
        self.assertEqual(res.id, doc.id)

    def test_search_by_id_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id("invalid"))

    def test_delete_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.delete_by_id("invalid"))


if __name__ == "__main__":
    unittest.main()
