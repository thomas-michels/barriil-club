import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company, UpdateCompany, CompanyMember
from app.crud.companies.models import CompanyModel, CompanyMember as CompanyMemberModel
from app.core.exceptions import NotFoundError, UnprocessableEntity


class TestCompanyServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = CompanyRepository()
        self.services = CompanyServices(self.repository)

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

    def test_create_company(self):
        company = self._build_company()
        result = asyncio.run(self.services.create(company))
        self.assertEqual(result.name, "ACME")
        self.assertEqual(CompanyModel.objects.count(), 1)

    def test_search_by_id(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id))
        self.assertEqual(res.id, doc.id)

    def test_search_by_id_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id("invalid"))

    def test_search_all(self):
        CompanyModel(**self._build_company("A").model_dump()).save()
        CompanyModel(**self._build_company("B").model_dump()).save()
        res = asyncio.run(self.services.search_all())
        self.assertEqual(len(res), 2)

    def test_update_company(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        updated = asyncio.run(
            self.services.update(doc.id, UpdateCompany(name="New ACME"))
        )
        self.assertEqual(updated.name, "New ACME")

    def test_update_company_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.update("invalid", UpdateCompany(name="New")))

    def test_delete_company(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        result = asyncio.run(self.services.delete_by_id(doc.id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(CompanyModel.objects(id=doc.id).first().is_active)

    def test_delete_company_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.delete_by_id("invalid"))

    def test_add_member(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        member = CompanyMember(user_id="usr1", role="owner")
        updated = asyncio.run(self.services.add_member(doc.id, member))
        self.assertEqual(len(updated.members), 1)
        self.assertEqual(updated.members[0].user_id, "usr1")

    def test_add_member_unique_user(self):
        c1 = CompanyModel(**self._build_company("One").model_dump())
        c1.save()
        c2 = CompanyModel(**self._build_company("Two").model_dump())
        c2.save()
        member = CompanyMember(user_id="usr1", role="owner")
        asyncio.run(self.services.add_member(c1.id, member))
        with self.assertRaises(UnprocessableEntity):
            asyncio.run(self.services.add_member(c2.id, member))

    def test_search_by_user(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.members.append(CompanyMemberModel(user_id="usr1", role="owner"))
        doc.save()
        res = asyncio.run(self.services.search_by_user("usr1"))
        self.assertEqual(res.id, doc.id)

    def test_search_by_user_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_user("usr1"))


if __name__ == "__main__":
    unittest.main()
