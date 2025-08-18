import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
from app.crud.addresses.schemas import Address
from app.core.exceptions import NotFoundError


class TestAddressRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

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
        repository = AddressRepository()
        address = self._build_address()
        result = asyncio.run(repository.create(address, company_id="com1"))
        self.assertEqual(result.postal_code, "12345")
        self.assertEqual(AddressModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = AddressModel(**self._build_address().model_dump(), company_id="com1")
        doc.save()
        repository = AddressRepository()
        res = asyncio.run(repository.select_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = AddressRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid", "com1"))

    def test_select_all(self):
        AddressModel(**self._build_address("1").model_dump(), company_id="com1").save()
        AddressModel(**self._build_address("2").model_dump(), company_id="com1").save()
        repository = AddressRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_address(self):
        doc = AddressModel(**self._build_address().model_dump(), company_id="com1")
        doc.save()
        repository = AddressRepository()
        updated = asyncio.run(
            repository.update(doc.id, doc.company_id, {"city": "New City"})
        )
        self.assertEqual(updated.city, "New City")

    def test_delete_address(self):
        doc = AddressModel(**self._build_address().model_dump(), company_id="com1")
        doc.save()
        repository = AddressRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(AddressModel.objects(id=doc.id).first().is_active)

    def test_delete_address_not_found(self):
        repository = AddressRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))

    def test_select_by_zip_code(self):
        doc = AddressModel(**self._build_address("12345").model_dump(), company_id="com1")
        doc.save()
        repository = AddressRepository()
        res = asyncio.run(repository.select_by_zip_code("12345", "com1"))
        self.assertEqual(res.id, doc.id)

    def test_select_by_zip_code_not_found(self):
        repository = AddressRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_zip_code("00000", "com1"))


if __name__ == "__main__":
    unittest.main()
