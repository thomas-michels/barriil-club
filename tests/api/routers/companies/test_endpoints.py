import asyncio
import unittest
from datetime import timedelta

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.companies import company_router
from app.api.dependencies.company import (
    ensure_user_without_company,
    require_company_member,
    require_user_company,
    require_company_owner,
)
from app.api.dependencies import decode_jwt
from app.api.composers.company_composite import company_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company, CompanyMember
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.services import AddressServices
from app.crud.addresses.schemas import Address
from app.crud.addresses.models import AddressModel
from app.crud.users.schemas import UserInDB
from app.core.utils.utc_datetime import UTCDateTime
from app.core.exceptions import NotFoundError


class TestCompanyEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = CompanyRepository()
        self.address_repo = AddressRepository()
        self.services = CompanyServices(self.repository, self.address_repo)
        self.address_services = AddressServices(self.address_repo)
        self.app = FastAPI()
        self.app.include_router(company_router, prefix="/api")

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
        self.company = asyncio.run(self.services.create(company))

        address = Address(
            postal_code="12345",
            street="Main",
            number="1",
            district="Center",
            city="City",
            state="ST",
        )
        self.address = asyncio.run(
            self.address_services.create(address, str(self.company.id))
        )
        self.user = UserInDB(
            user_id="usr1",
            email="u@t.com",
            name="U",
            nickname="u",
            picture=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        async def override_ensure_user_without_company():
            return self.user

        async def override_require_user_company():
            return self.company

        async def override_require_company_member(company_id: str):
            return self.company

        async def override_company_composer():
            return self.services

        async def override_require_company_owner(company_id: str):
            return self.company

        self.app.dependency_overrides[ensure_user_without_company] = (
            override_ensure_user_without_company
        )
        self.app.dependency_overrides[require_user_company] = override_require_user_company
        self.app.dependency_overrides[require_company_member] = override_require_company_member
        self.app.dependency_overrides[require_company_owner] = override_require_company_owner
        self.app.dependency_overrides[company_composer] = override_company_composer

        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _build_company_payload(self, name: str = "Beta", use_address: bool = True) -> dict:
        payload = {
            "name": name,
            "phone_number": "9999-9999",
            "ddd": "11",
            "email": "info@beta.com",
        }
        if use_address:
            payload["addressId"] = self.address.id
        return payload

    def test_create_company_endpoint(self):
        resp = self.client.post(
            "/api/companies", json=self._build_company_payload("NewCo")
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()["data"]
        self.assertEqual(data["name"], "NewCo")
        self.assertEqual(len(data["members"]), 1)
        self.assertEqual(data["members"][0]["userId"], self.user.user_id)
        self.assertEqual(data["members"][0]["role"], "owner")
        self.assertIn("subscription", data)

    def test_create_company_endpoint_without_address(self):
        resp = self.client.post(
            "/api/companies", json=self._build_company_payload("NoAddr", use_address=False)
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()["data"]
        self.assertEqual(data["name"], "NoAddr")
        self.assertIsNone(data.get("addressId"))

    def test_get_company_by_id(self):
        resp = self.client.get(f"/api/companies/{self.company.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], str(self.company.id))

    def test_list_companies(self):
        resp = self.client.get("/api/companies")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)

    def test_update_company_endpoint(self):
        resp = self.client.put(
            f"/api/companies/{self.company.id}", json={"name": "Updated"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["name"], "Updated")

    def test_delete_company_endpoint(self):
        resp = self.client.delete(f"/api/companies/{self.company.id}")
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id(self.company.id))

    def test_add_member_endpoint(self):
        payload = {"user_id": "usr2", "role": "member"}
        resp = self.client.post(
            f"/api/companies/{self.company.id}/members", json=payload
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]["members"]), 1)
        self.assertEqual(resp.json()["data"]["members"][0]["userId"], "usr2")

    def test_add_member_forbidden(self):
        self.app.dependency_overrides.pop(require_company_owner, None)
        self.app.dependency_overrides.pop(require_company_member, None)

        async def override_decode_jwt():
            return self.user

        self.app.dependency_overrides[decode_jwt] = override_decode_jwt
        asyncio.run(
            self.services.add_member(
                self.company.id, CompanyMember(user_id=self.user.user_id, role="member")
            )
        )
        payload = {"user_id": "usr2", "role": "member"}
        resp = self.client.post(
            f"/api/companies/{self.company.id}/members", json=payload
        )
        self.assertEqual(resp.status_code, 403)

    def test_remove_member_endpoint(self):
        payload = {"user_id": "usr2", "role": "member"}
        asyncio.run(self.services.add_member(self.company.id, CompanyMember(**payload)))
        resp = self.client.delete(
            f"/api/companies/{self.company.id}/members/usr2"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]["members"]), 0)

    def test_remove_member_forbidden(self):
        self.app.dependency_overrides.pop(require_company_owner, None)

        async def override_decode_jwt():
            return self.user

        self.app.dependency_overrides[decode_jwt] = override_decode_jwt
        asyncio.run(
            self.services.add_member(
                self.company.id, CompanyMember(user_id=self.user.user_id, role="member")
            )
        )
        asyncio.run(
            self.services.add_member(
                self.company.id, CompanyMember(user_id="usr2", role="member")
            )
        )
        resp = self.client.delete(
            f"/api/companies/{self.company.id}/members/usr2"
        )
        self.assertEqual(resp.status_code, 403)

    def test_leave_company_endpoint(self):
        asyncio.run(
            self.services.add_member(
                self.company.id, CompanyMember(user_id="owner", role="owner")
            )
        )
        asyncio.run(
            self.services.add_member(
                self.company.id, CompanyMember(user_id=self.user.user_id, role="member")
            )
        )
        self.company = asyncio.run(self.services.search_by_id(self.company.id))
        async def override_decode_jwt():
            return self.user
        self.app.dependency_overrides[decode_jwt] = override_decode_jwt
        resp = self.client.delete(
            f"/api/companies/{self.company.id}/members/me"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]["members"]), 1)
        self.assertEqual(resp.json()["data"]["members"][0]["userId"], "owner")

    def test_leave_company_owner_forbidden(self):
        asyncio.run(
            self.services.add_member(
                self.company.id,
                CompanyMember(user_id=self.user.user_id, role="owner"),
            )
        )
        self.company = asyncio.run(self.services.search_by_id(self.company.id))
        async def override_decode_jwt():
            return self.user
        self.app.dependency_overrides[decode_jwt] = override_decode_jwt
        resp = self.client.delete(
            f"/api/companies/{self.company.id}/members/me"
        )
        self.assertEqual(resp.status_code, 403)

    def test_get_subscription_endpoint(self):
        resp = self.client.get(f"/api/companies/{self.company.id}/subscription")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["data"]["isActive"])

    def test_update_subscription_endpoint(self):
        new_date = UTCDateTime.now() + timedelta(days=15)
        resp = self.client.put(
            f"/api/companies/{self.company.id}/subscription",
            json={"isActive": False, "expiresAt": str(new_date)},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertFalse(data["isActive"])
        self.assertEqual(data["expiresAt"], str(new_date))


if __name__ == "__main__":
    unittest.main()
