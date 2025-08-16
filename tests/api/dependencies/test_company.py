import asyncio
import unittest

import mongomock
from fastapi import HTTPException
from mongoengine import connect, disconnect

from app.api.dependencies.company import (
    ensure_user_without_company,
    require_company_member,
    require_user_company,
)
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.models import CompanyModel, CompanyMember
from app.crud.companies.schemas import Company
from app.crud.users.schemas import UserInDB


class TestCompanyDependencies(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def _build_company(self, name: str = "ACME") -> Company:
        return Company(
            name=name,
            address_line1="Street 1",
            address_line2="Apt 2",
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )

    def _build_user(self, uid: str = "usr1") -> UserInDB:
        return UserInDB(
            user_id=uid,
            email="u@t.com",
            name="U",
            nickname="u",
            picture=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

    def test_ensure_user_without_company_allows(self):
        services = CompanyServices(CompanyRepository())
        user = self._build_user()
        res = asyncio.run(ensure_user_without_company(user, services))
        self.assertEqual(res.user_id, user.user_id)

    def test_ensure_user_without_company_denies(self):
        company = CompanyModel(**self._build_company().model_dump())
        company.members.append(CompanyMember(user_id="usr1", role="owner"))
        company.save()
        services = CompanyServices(CompanyRepository())
        user = self._build_user()
        with self.assertRaises(HTTPException):
            asyncio.run(ensure_user_without_company(user, services))

    def test_require_user_company(self):
        company = CompanyModel(**self._build_company().model_dump())
        company.members.append(CompanyMember(user_id="usr1", role="owner"))
        company.save()
        services = CompanyServices(CompanyRepository())
        user = self._build_user()
        res = asyncio.run(require_user_company(user, services))
        self.assertEqual(res.id, company.id)

    def test_require_company_member_denies(self):
        company = CompanyModel(**self._build_company().model_dump())
        company.save()
        services = CompanyServices(CompanyRepository())
        user = self._build_user()
        with self.assertRaises(HTTPException):
            asyncio.run(require_company_member(company.id, user, services))

    def test_require_company_member_allows(self):
        company = CompanyModel(**self._build_company().model_dump())
        company.members.append(CompanyMember(user_id="usr1", role="owner"))
        company.save()
        services = CompanyServices(CompanyRepository())
        user = self._build_user()
        res = asyncio.run(require_company_member(company.id, user, services))
        self.assertEqual(res.id, company.id)


if __name__ == "__main__":
    unittest.main()
