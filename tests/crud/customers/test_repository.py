import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.customers.repositories import CustomerRepository
from app.crud.customers.models import CustomerModel
from app.crud.customers.schemas import Customer
from app.core.exceptions import NotFoundError, UnprocessableEntity


class TestCustomerRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def _build_customer(self, document: str = "10000000019") -> Customer:
        return Customer(
            name="John Doe",
            document=document,
            email="john@example.com",
            mobile="999",
            birth_date="1990-01-01",
            address_ids=["add1"],
            notes="VIP",
        )

    def test_create_customer(self):
        repository = CustomerRepository()
        customer = self._build_customer()
        result = asyncio.run(repository.create(customer))
        self.assertEqual(result.document, "10000000019")
        self.assertEqual(CustomerModel.objects.count(), 1)

    def test_create_customer_unique_document(self):
        repository = CustomerRepository()
        asyncio.run(repository.create(self._build_customer("10000000019")))
        with self.assertRaises(UnprocessableEntity):
            asyncio.run(repository.create(self._build_customer("10000000019")))

    def test_create_customer_more_than_five_addresses(self):
        repository = CustomerRepository()
        customer = self._build_customer()
        customer.address_ids = [f"add{i}" for i in range(6)]
        with self.assertRaises(UnprocessableEntity):
            asyncio.run(repository.create(customer))

    def test_select_by_id_found(self):
        doc = CustomerModel(**self._build_customer().model_dump())
        doc.save()
        repository = CustomerRepository()
        res = asyncio.run(repository.select_by_id(doc.id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = CustomerRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid"))

    def test_select_all(self):
        CustomerModel(**self._build_customer("10000000108").model_dump()).save()
        CustomerModel(**self._build_customer("10000000280").model_dump()).save()
        repository = CustomerRepository()
        res = asyncio.run(repository.select_all())
        self.assertEqual(len(res), 2)

    def test_update_customer(self):
        doc = CustomerModel(**self._build_customer().model_dump())
        doc.save()
        repository = CustomerRepository()
        updated = asyncio.run(repository.update(doc.id, {"name": "New"}))
        self.assertEqual(updated.name, "New")

    def test_delete_customer(self):
        doc = CustomerModel(**self._build_customer().model_dump())
        doc.save()
        repository = CustomerRepository()
        result = asyncio.run(repository.delete_by_id(doc.id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(CustomerModel.objects(id=doc.id).first().is_active)

    def test_delete_customer_not_found(self):
        repository = CustomerRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid"))


if __name__ == "__main__":
    unittest.main()
