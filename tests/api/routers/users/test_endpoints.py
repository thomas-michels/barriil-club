import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers.users import user_router
from app.api.dependencies.auth import decode_jwt
from app.api.composers.company_composite import company_composer
from app.crud.users.schemas import UserInDB
from app.crud.companies.schemas import CompanyInDB


class TestUserEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        self.user = UserInDB(
            user_id="usr1",
            email="u@t.com",
            name="U",
            nickname="u",
            picture=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        self.company = CompanyInDB(
            id="cmp1",
            name="ACME",
            address_id="add1",
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
            members=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.app = FastAPI()
        self.app.include_router(user_router, prefix="/api")

        async def override_decode_jwt():
            return self.user

        class CompanyServiceStub:
            def __init__(self, company):
                self.company = company

            async def search_by_user(self, user_id: str):
                return self.company

        async def override_company_composer():
            return CompanyServiceStub(self.company)

        self.app.dependency_overrides[decode_jwt] = override_decode_jwt
        self.app.dependency_overrides[company_composer] = override_company_composer

        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}

    def test_get_current_user_returns_company(self):
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(data["userId"], self.user.user_id)
        self.assertEqual(data["company"]["id"], self.company.id)


if __name__ == "__main__":
    unittest.main()
