import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.customers import customer_router
from app.api.dependencies.company import require_company_member, require_user_company
from app.api.composers.customer_composite import customer_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
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
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = CustomerRepository()
        self.services = CustomerServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(customer_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_require_company_member(company_id: str):
            return self.company

        async def override_customer_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[require_company_member] = (
            override_require_company_member
        )
        self.app.dependency_overrides[customer_composer] = override_customer_composer
        self.client = TestClient(self.app)

        seed_address = AddressModel(
            postal_code="00000",
            street="Seed",
            number="1",
            district="Seed",
            city="Seed",
            state="SS",
            company_id="seed",
        )
        seed_address.save()
        self.address_id = str(seed_address.id)
        company = Company(
            name="ACME",
            address_id=self.address_id,
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )
        self.company = asyncio.run(self.company_services.create(company))

        customer = Customer(
            name="John",
            document="10000000019",
            email="john@example.com",
            mobile="999",
            birth_date="1990-01-01",
            address_ids=[self.address_id],
            notes="VIP",
            company_id=str(self.company.id),
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
            "addressIds": [self.address_id],
            "notes": "Note",
            "companyId": str(self.company.id),
        }

    def test_create_customer_endpoint(self):
        resp = self.client.post("/api/customers", json=self._payload("10000000280"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["document"], "10000000280")

    def test_get_customer_by_id(self):
        resp = self.client.get(
            f"/api/customers/{self.customer.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.customer.id)

    def test_list_customers(self):
        resp = self.client.get(
            "/api/customers", params={"company_id": str(self.company.id)}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_customer_endpoint(self):
        resp = self.client.put(
            f"/api/customers/{self.customer.id}",
            params={"company_id": str(self.company.id)},
            json={"name": "Updated"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["name"], "Updated")

    def test_delete_customer_endpoint(self):
        resp = self.client.delete(
            f"/api/customers/{self.customer.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.search_by_id(self.customer.id, str(self.company.id))
            )

    def test_create_customer_returns_400_when_not_created(self):
        async def fake_create(customer):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/customers", json=self._payload("10000000361"))
        self.assertEqual(resp.status_code, 400)

    def test_update_customer_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, customer):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/customers/{self.customer.id}",
            params={"company_id": str(self.company.id)},
            json={"name": "Fail"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_customer_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(
            f"/api/customers/{self.customer.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
