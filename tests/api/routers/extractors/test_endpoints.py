import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.extractors import extractor_router
from app.api.dependencies.company import require_company_member, require_user_company
from app.api.composers.extractor_composite import extractor_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
from app.crud.extractors.repositories import ExtractorRepository
from app.crud.extractors.services import ExtractorServices
from app.crud.extractors.schemas import Extractor
from app.core.exceptions import NotFoundError


class TestExtractorEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.extractor_repo = ExtractorRepository()
        self.extractor_services = ExtractorServices(self.extractor_repo)

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
        extractor = Extractor(brand="Old", company_id=str(self.company.id))
        self.extractor = asyncio.run(self.extractor_services.create(extractor))

        self.app = FastAPI()
        self.app.include_router(extractor_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_require_company_member(company_id: str):
            return self.company

        async def override_extractor_composer():
            return self.extractor_services

        self.app.dependency_overrides[require_user_company] = override_require_user_company
        self.app.dependency_overrides[require_company_member] = override_require_company_member
        self.app.dependency_overrides[extractor_composer] = override_extractor_composer

        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def test_create_extractor_endpoint(self):
        payload = {"brand": "New", "company_id": str(self.company.id)}
        resp = self.client.post("/api/extractors", json=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["brand"], "New")

    def test_get_extractor_by_id(self):
        resp = self.client.get(
            f"/api/extractors/{self.extractor.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], str(self.extractor.id))

    def test_list_extractors(self):
        resp = self.client.get(
            "/api/extractors", params={"company_id": str(self.company.id)}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_extractor_endpoint(self):
        resp = self.client.put(
            f"/api/extractors/{self.extractor.id}",
            params={"company_id": str(self.company.id)},
            json={"brand": "Updated"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["brand"], "Updated")

    def test_delete_extractor_endpoint(self):
        resp = self.client.delete(
            f"/api/extractors/{self.extractor.id}",
            params={"company_id": str(self.company.id)},
        )
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.extractor_services.search_by_id(self.extractor.id, str(self.company.id))
            )


if __name__ == "__main__":
    unittest.main()
