import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.beer_types import beer_type_router
from app.api.dependencies.company import require_user_company
from app.api.composers.beer_type_composite import beer_type_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
from app.crud.beer_types.repositories import BeerTypeRepository
from app.crud.beer_types.services import BeerTypeServices
from app.crud.beer_types.schemas import BeerType
from app.core.exceptions import NotFoundError


class TestBeerTypeEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = BeerTypeRepository()
        self.services = BeerTypeServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(beer_type_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_beer_type_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[beer_type_composer] = override_beer_type_composer
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

        beer_type = BeerType(
            name="Pale Ale",
            producer="Brew Co",
            abv=5.0,
            ibu=40.0,
            description="Tasty",
            default_sale_price_per_l=10.0,
        )
        self.beer_type = asyncio.run(
            self.services.create(beer_type, company_id=str(self.company.id))
        )

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, name: str = "Lager") -> dict:
        return {
            "name": name,
            "producer": "Brew Co",
            "abv": 4.5,
            "ibu": 20.0,
            "description": "Desc",
            "defaultSalePricePerL": 9.0,
        }

    def test_create_beer_type_endpoint(self):
        resp = self.client.post("/api/beer-types", json=self._payload("IPA"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["name"], "IPA")

    def test_get_beer_type_by_id(self):
        resp = self.client.get(f"/api/beer-types/{self.beer_type.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.beer_type.id)

    def test_list_beer_types(self):
        resp = self.client.get("/api/beer-types")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_beer_type_endpoint(self):
        resp = self.client.put(
            f"/api/beer-types/{self.beer_type.id}",
            json={"name": "New"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["name"], "New")

    def test_delete_beer_type_endpoint(self):
        resp = self.client.delete(f"/api/beer-types/{self.beer_type.id}")
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.search_by_id(self.beer_type.id, str(self.company.id))
            )

    def test_create_beer_type_returns_400_when_not_created(self):
        async def fake_create(beer_type, company_id):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/beer-types", json=self._payload("Fail"))
        self.assertEqual(resp.status_code, 400)

    def test_update_beer_type_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, beer_type):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/beer-types/{self.beer_type.id}",
            json={"name": "Fail"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_beer_type_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(f"/api/beer-types/{self.beer_type.id}")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
