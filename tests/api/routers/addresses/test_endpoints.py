import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.addresses import address_router
from app.api.composers.address_composite import address_composer
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.services import AddressServices
from app.crud.addresses.schemas import Address
from app.core.exceptions import NotFoundError


class TestAddressEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = AddressRepository()
        self.services = AddressServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(address_router, prefix="/api")

        async def override_address_composer():
            return self.services

        self.app.dependency_overrides[address_composer] = override_address_composer
        self.client = TestClient(self.app)

        address = Address(
            postal_code="12345",
            street="Main",
            number="1",
            complement="Apt",
            district="Center",
            city="City",
            state="ST",
            reference="Near",
        )
        self.address = asyncio.run(self.services.create(address))

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, postal_code: str = "99999") -> dict:
        return {
            "postalCode": postal_code,
            "street": "Street",
            "number": "10",
            "complement": "Apt",
            "district": "Dist",
            "city": "Metropolis",
            "state": "ST",
            "reference": "Ref",
        }

    def test_create_address_endpoint(self):
        resp = self.client.post("/api/addresses", json=self._payload("11111"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["postal_code"], "11111")

    def test_get_address_by_id(self):
        resp = self.client.get(f"/api/addresses/{self.address.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.address.id)

    def test_list_addresses(self):
        resp = self.client.get("/api/addresses")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_address_endpoint(self):
        resp = self.client.put(
            f"/api/addresses/{self.address.id}", json={"city": "New"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["city"], "New")

    def test_delete_address_endpoint(self):
        resp = self.client.delete(f"/api/addresses/{self.address.id}")
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id(self.address.id))

    def test_create_address_returns_400_when_not_created(self):
        async def fake_create(address):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/addresses", json=self._payload("22222"))
        self.assertEqual(resp.status_code, 400)

    def test_update_address_returns_400_when_not_updated(self):
        async def fake_update(id, address):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/addresses/{self.address.id}", json={"city": "Fail"}
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_address_returns_400_when_not_deleted(self):
        async def fake_delete(id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(f"/api/addresses/{self.address.id}")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
