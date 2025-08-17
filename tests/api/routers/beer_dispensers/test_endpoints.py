import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.beer_dispensers import beer_dispenser_router
from app.api.dependencies.company import require_company_member, require_user_company
from app.api.composers.beer_dispenser_composite import beer_dispenser_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.beer_dispensers.services import BeerDispenserServices
from app.crud.beer_dispensers.schemas import BeerDispenser, DispenserStatus, Voltage
from app.core.exceptions import NotFoundError


class TestBeerDispenserEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = BeerDispenserRepository()
        self.services = BeerDispenserServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(beer_dispenser_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_require_company_member(company_id: str):
            return self.company

        async def override_dispenser_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[require_company_member] = (
            override_require_company_member
        )
        self.app.dependency_overrides[beer_dispenser_composer] = (
            override_dispenser_composer
        )
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
        company = Company(
            name="ACME",
            address_id=str(seed_address.id),
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )
        self.company = asyncio.run(self.company_services.create(company))

        dispenser = BeerDispenser(
            brand="Acme",
            model="X1",
            serial_number="SN1",
            taps_count=4,
            voltage=Voltage.V110,
            status=DispenserStatus.ACTIVE,
            notes="",
            company_id=str(self.company.id),
        )
        self.dispenser = asyncio.run(self.services.create(dispenser))

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, brand: str = "NewBrand") -> dict:
        return {
            "brand": brand,
            "model": "X2",
            "serialNumber": "SN2",
            "tapsCount": 2,
            "voltage": "110V",
            "status": "ACTIVE",
            "companyId": str(self.company.id),
        }

    def test_create_dispenser_endpoint(self):
        resp = self.client.post("/api/beer-dispensers", json=self._payload("BrandX"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["brand"], "BrandX")

    def test_get_dispenser_by_id(self):
        resp = self.client.get(
            f"/api/beer-dispensers/{self.dispenser.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.dispenser.id)

    def test_list_dispensers(self):
        resp = self.client.get(
            "/api/beer-dispensers", params={"company_id": str(self.company.id)}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_dispenser_endpoint(self):
        resp = self.client.put(
            f"/api/beer-dispensers/{self.dispenser.id}",
            params={"company_id": str(self.company.id)},
            json={"brand": "Updated"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["brand"], "Updated")

    def test_delete_dispenser_endpoint(self):
        resp = self.client.delete(
            f"/api/beer-dispensers/{self.dispenser.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.search_by_id(self.dispenser.id, str(self.company.id))
            )

    def test_create_dispenser_returns_400_when_not_created(self):
        async def fake_create(dispenser):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/beer-dispensers", json=self._payload("Fail"))
        self.assertEqual(resp.status_code, 400)

    def test_update_dispenser_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, dispenser):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/beer-dispensers/{self.dispenser.id}",
            params={"company_id": str(self.company.id)},
            json={"brand": "Fail"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_dispenser_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(
            f"/api/beer-dispensers/{self.dispenser.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
