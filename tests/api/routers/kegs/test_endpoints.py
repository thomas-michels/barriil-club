import asyncio
import unittest

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.kegs import keg_router
from app.api.dependencies.company import require_user_company
from app.api.composers.keg_composite import keg_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
from app.crud.beer_types.models import BeerTypeModel
from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.services import KegServices
from app.crud.kegs.schemas import Keg, KegStatus
from app.core.exceptions import NotFoundError


class TestKegEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = KegRepository()
        self.services = KegServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(keg_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_keg_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[keg_composer] = override_keg_composer
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

        self.beer_type = BeerTypeModel(
            name="Pale Ale",
            company_id=str(self.company.id),
        )
        self.beer_type.save()

        keg = Keg(
            number="1",
            size_l=50,
            beer_type_id=str(self.beer_type.id),
            cost_price_per_l=5.0,
            sale_price_per_l=8.0,
            lot="L1",
            expiration_date=None,
            current_volume_l=25.0,
            status=KegStatus.AVAILABLE,
            notes="",
        )
        self.keg = asyncio.run(
            self.services.create(keg, str(self.company.id))
        )

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, number: str = "2") -> dict:
        return {
            "number": number,
            "sizeL": 50,
            "beerTypeId": str(self.beer_type.id),
            "costPricePerL": 5.0,
            "salePricePerL": 8.0,
            "lot": "L2",
            "currentVolumeL": 25.0,
            "status": "AVAILABLE",
        }

    def test_create_keg_endpoint(self):
        resp = self.client.post("/api/kegs", json=self._payload("3"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["number"], "3")

    def test_get_keg_by_id(self):
        resp = self.client.get(f"/api/kegs/{self.keg.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.keg.id)

    def test_list_kegs(self):
        resp = self.client.get("/api/kegs")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_list_kegs_filtered_by_status(self):
        other_keg = Keg(
            number="2",
            size_l=50,
            beer_type_id=str(self.beer_type.id),
            cost_price_per_l=5.0,
            sale_price_per_l=8.0,
            lot="L2",
            expiration_date=None,
            current_volume_l=25.0,
            status=KegStatus.IN_USE,
            notes="",
        )
        asyncio.run(self.services.create(other_keg, str(self.company.id)))
        resp = self.client.get(
            "/api/kegs", params={"status": KegStatus.AVAILABLE.value}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]), 1)
        self.assertEqual(resp.json()["data"][0]["id"], self.keg.id)

    def test_update_keg_endpoint(self):
        resp = self.client.put(
            f"/api/kegs/{self.keg.id}",
            json={"number": "10"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["number"], "10")

    def test_delete_keg_endpoint(self):
        resp = self.client.delete(f"/api/kegs/{self.keg.id}")
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id(self.keg.id, str(self.company.id)))

    def test_create_keg_returns_400_when_not_created(self):
        async def fake_create(keg, company_id):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/kegs", json=self._payload("4"))
        self.assertEqual(resp.status_code, 400)

    def test_update_keg_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, keg):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/kegs/{self.keg.id}",
            json={"number": "11"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_keg_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(f"/api/kegs/{self.keg.id}")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
