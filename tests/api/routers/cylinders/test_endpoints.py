import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.cylinders import cylinder_router
from app.api.dependencies.company import require_user_company
from app.api.composers.cylinder_composite import cylinder_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
from app.crud.cylinders.repositories import CylinderRepository
from app.crud.cylinders.services import CylinderServices
from app.crud.cylinders.schemas import Cylinder, CylinderStatus
from app.core.exceptions import NotFoundError


class TestCylinderEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = CylinderRepository()
        self.services = CylinderServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(cylinder_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_cylinder_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[cylinder_composer] = override_cylinder_composer
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

        cylinder = Cylinder(
            brand="Acme",
            weight_kg=10.5,
            number="CY1",
            status=CylinderStatus.AVAILABLE,
            notes="",
        )
        self.cylinder = asyncio.run(
            self.services.create(cylinder, str(self.company.id))
        )

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, brand: str = "NewBrand", number: str = "CY2") -> dict:
        return {
            "brand": brand,
            "weightKg": 10.5,
            "number": number,
            "status": "AVAILABLE",
        }

    def test_create_cylinder_endpoint(self):
        resp = self.client.post("/api/cylinders", json=self._payload("BrandX"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["brand"], "BrandX")

    def test_get_cylinder_by_id(self):
        resp = self.client.get(
            f"/api/cylinders/{self.cylinder.id}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.cylinder.id)

    def test_list_cylinders(self):
        resp = self.client.get(
            "/api/cylinders"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_cylinder_endpoint(self):
        resp = self.client.put(
            f"/api/cylinders/{self.cylinder.id}",
            json={"brand": "Updated"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["brand"], "Updated")

    def test_delete_cylinder_endpoint(self):
        resp = self.client.delete(
            f"/api/cylinders/{self.cylinder.id}"
        )
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.search_by_id(self.cylinder.id, str(self.company.id))
            )

    def test_create_cylinder_returns_400_when_not_created(self):
        async def fake_create(cylinder, company_id):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/cylinders", json=self._payload("Fail"))
        self.assertEqual(resp.status_code, 400)

    def test_update_cylinder_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, cylinder):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/cylinders/{self.cylinder.id}",
            json={"brand": "Fail"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_cylinder_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(
            f"/api/cylinders/{self.cylinder.id}"
        )
        self.assertEqual(resp.status_code, 400)

    def test_list_cylinders_returns_empty_list_when_not_found(self):
        async def fake_search_all(company_id):
            raise NotFoundError("Cylinders not found")

        self.services.search_all = fake_search_all
        resp = self.client.get("/api/cylinders")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"], [])

    def test_create_cylinder_appends_suffix_when_duplicate(self):
        resp = self.client.post(
            "/api/cylinders",
            json=self._payload(number=self.cylinder.number),
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(
            resp.json()["data"]["number"], f"{self.cylinder.number}1"
        )


if __name__ == "__main__":
    unittest.main()
