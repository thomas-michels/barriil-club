import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.composers.extraction_kit_composite import extraction_kit_composer
from app.api.dependencies.company import require_user_company
from app.api.routers.extraction_kits import extraction_kit_router
from app.core.exceptions import NotFoundError
from app.crud.addresses.models import AddressModel
from app.crud.addresses.repositories import AddressRepository
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.schemas import Company
from app.crud.companies.services import CompanyServices
from app.crud.extraction_kits.repositories import ExtractionKitRepository
from app.crud.extraction_kits.schemas import (
    ExtractionKit,
    ExtractionKitStatus,
    ExtractionKitType,
)
from app.crud.extraction_kits.services import ExtractionKitServices


class TestExtractionKitEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = ExtractionKitRepository()
        self.services = ExtractionKitServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(extraction_kit_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_gauge_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[extraction_kit_composer] = override_gauge_composer
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

        gauge = ExtractionKit(
            brand="Acme",
            type=ExtractionKitType.SIMPLE,
            serial_number="SN1",
            last_calibration_date=None,
            status=ExtractionKitStatus.ACTIVE,
            notes="",
        )
        self.gauge = asyncio.run(
            self.services.create(gauge, company_id=str(self.company.id))
        )

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, brand: str = "NewBrand") -> dict:
        return {
            "brand": brand,
            "type": "SIMPLE",
            "serialNumber": "SN2",
            "status": "ACTIVE",
        }

    def test_create_gauge_endpoint(self):
        resp = self.client.post("/api/extraction-kits", json=self._payload("BrandX"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["brand"], "BrandX")

    def test_get_gauge_by_id(self):
        resp = self.client.get(f"/api/extraction-kits/{self.gauge.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.gauge.id)

    def test_list_gauges(self):
        resp = self.client.get("/api/extraction-kits")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_gauge_endpoint(self):
        resp = self.client.put(
            f"/api/extraction-kits/{self.gauge.id}",
            json={"brand": "Updated"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["brand"], "Updated")

    def test_delete_gauge_endpoint(self):
        resp = self.client.delete(f"/api/extraction-kits/{self.gauge.id}")
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id(self.gauge.id, str(self.company.id)))

    def test_create_gauge_returns_400_when_not_created(self):
        async def fake_create(gauge, company_id):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/extraction-kits", json=self._payload("Fail"))
        self.assertEqual(resp.status_code, 400)

    def test_update_gauge_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, gauge):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/extraction-kits/{self.gauge.id}",
            json={"brand": "Fail"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_gauge_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(f"/api/extraction-kits/{self.gauge.id}")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
