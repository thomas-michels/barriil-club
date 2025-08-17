import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers.users import user_router
from app.api.dependencies import decode_jwt
from app.api.composers.user_composite import user_composer
from app.crud.users.schemas import UserInDB


class FakeUserServices:
    async def search_by_email(self, email: str):
        if email == "test@example.com":
            return UserInDB(
                user_id="id-123",
                email="test@example.com",
                name="Test",
                nickname="test",
                picture=None,
                user_metadata=None,
                app_metadata={},
                last_login=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        return None


class TestUserEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.include_router(user_router, prefix="/api")

        async def override_decode_jwt():
            return UserInDB(
                user_id="usr1",
                email="u@t.com",
                name="User",
                nickname="user",
                picture=None,
                user_metadata=None,
                app_metadata={},
                last_login=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )

        async def override_user_composer():
            return FakeUserServices()

        self.app.dependency_overrides[decode_jwt] = override_decode_jwt
        self.app.dependency_overrides[user_composer] = override_user_composer

        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}

    def test_get_user_by_email_found(self):
        resp = self.client.get("/api/users/email/test@example.com")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["email"], "test@example.com")

    def test_get_user_by_email_not_found(self):
        resp = self.client.get("/api/users/email/unknown@example.com")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
