import asyncio
import unittest
from unittest.mock import patch

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.addresses import address_router
from app.api.dependencies.company import require_user_company
from app.api.composers.address_composite import address_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.services import AddressServices
from app.crud.addresses.schemas import Address
from app.crud.addresses.models import AddressModel
from app.core.exceptions import NotFoundError


class TestAddressEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = self.address_repo
        self.services = AddressServices(self.repository)
        self.app = FastAPI()
        self.app.include_router(address_router, prefix="/api")

        async def override_require_user_company():
            return self.company

        async def override_address_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[address_composer] = override_address_composer
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
        self.address = asyncio.run(
            self.services.create(address, company_id=str(self.company.id))
        )

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
            f"/api/addresses/{self.address.id}",
            json={"city": "New"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["city"], "New")

    def test_delete_address_endpoint(self):
        resp = self.client.delete(f"/api/addresses/{self.address.id}")
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.search_by_id(self.address.id, str(self.company.id))
            )

    @patch("app.api.dependencies.get_address_by_zip_code.get_address_by_zip_code")
    def test_get_address_by_zip_always_via_cep(self, mock_get):
        mock_get.return_value = {
            "cep": "99999-000",
            "logradouro": "Street",
            "complemento": "",
            "bairro": "Neighborhood",
            "localidade": "City",
            "uf": "ST",
        }
        resp = self.client.get(
            f"/api/addresses/zip/{self.address.postal_code}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["postalCode"], "99999-000")
        mock_get.assert_called_once()

    def test_create_address_returns_400_when_not_created(self):
        async def fake_create(address, company_id):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/addresses", json=self._payload("22222"))
        self.assertEqual(resp.status_code, 400)

    def test_update_address_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, address):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/addresses/{self.address.id}",
            json={"city": "Fail"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_address_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(f"/api/addresses/{self.address.id}")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
