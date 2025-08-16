import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.customers import customer_router
from app.api.composers.customer_composite import customer_composer
from app.crud.customers.repositories import CustomerRepository
from app.crud.customers.services import CustomerServices
from app.crud.customers.schemas import Customer
from app.core.exceptions import NotFoundError


class TestCustomerEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = CustomerRepository()
        self.services = CustomerServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(customer_router, prefix="/api")

        async def override_customer_composer():
            return self.services

        self.app.dependency_overrides[customer_composer] = override_customer_composer
        self.client = TestClient(self.app)

        customer = Customer(
            name="John",
            document="10000000019",
            email="john@example.com",
            mobile="999",
            birth_date="1990-01-01",
            address_ids=["add1"],
            notes="VIP",
        )
        self.customer = asyncio.run(self.services.create(customer))

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, document: str = "10000000108") -> dict:
        return {
            "name": "Jane",
            "document": document,
            "email": "jane@example.com",
            "mobile": "888",
            "birthDate": "1995-01-01",
            "addressIds": ["add1"],
            "notes": "Note",
        }

    def test_create_customer_endpoint(self):
        resp = self.client.post("/api/customers", json=self._payload("10000000280"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["document"], "10000000280")

    def test_get_customer_by_id(self):
        resp = self.client.get(f"/api/customers/{self.customer.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.customer.id)

    def test_list_customers(self):
        resp = self.client.get("/api/customers")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_customer_endpoint(self):
        resp = self.client.put(
            f"/api/customers/{self.customer.id}", json={"name": "Updated"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["name"], "Updated")

    def test_delete_customer_endpoint(self):
        resp = self.client.delete(f"/api/customers/{self.customer.id}")
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id(self.customer.id))

    def test_create_customer_returns_400_when_not_created(self):
        async def fake_create(customer):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/customers", json=self._payload("10000000361"))
        self.assertEqual(resp.status_code, 400)

    def test_update_customer_returns_400_when_not_updated(self):
        async def fake_update(id, customer):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/customers/{self.customer.id}", json={"name": "Fail"}
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_customer_returns_400_when_not_deleted(self):
        async def fake_delete(id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(f"/api/customers/{self.customer.id}")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
