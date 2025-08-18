import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.customers.repositories import CustomerRepository
from app.crud.customers.services import CustomerServices
from app.crud.customers.schemas import Customer, UpdateCustomer
from app.crud.customers.models import CustomerModel
from app.core.exceptions import NotFoundError, UnprocessableEntity


class TestCustomerServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = CustomerRepository()
        self.services = CustomerServices(self.repository)

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
        customer = self._build_customer()
        result = asyncio.run(
            self.services.create(customer, company_id="com1")
        )
        self.assertEqual(result.document, "10000000019")

    def test_create_customer_unique_document(self):
        asyncio.run(
            self.services.create(self._build_customer("10000000019"), company_id="com1")
        )
        with self.assertRaises(UnprocessableEntity):
            asyncio.run(
                self.services.create(self._build_customer("10000000019"), company_id="com1")
            )

    def test_search_by_id(self):
        doc = CustomerModel(**self._build_customer().model_dump(), company_id="com1")
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        CustomerModel(**self._build_customer("10000000108").model_dump(), company_id="com1").save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 1)

    def test_update_customer(self):
        doc = CustomerModel(**self._build_customer().model_dump(), company_id="com1")
        doc.save()
        updated = asyncio.run(
            self.services.update(doc.id, doc.company_id, UpdateCustomer(name="New"))
        )
        self.assertEqual(updated.name, "New")

    def test_delete_customer(self):
        doc = CustomerModel(**self._build_customer().model_dump(), company_id="com1")
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
