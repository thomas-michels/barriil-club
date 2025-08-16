import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.models import CompanyModel
from app.crud.companies.schemas import Company, CompanyMember
from app.core.exceptions import NotFoundError, UnprocessableEntity


class TestCompanyRepository(unittest.TestCase):
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
            address_id="add1",
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )

    def test_create_company(self):
        repository = CompanyRepository()
        company = self._build_company()
        result = asyncio.run(repository.create(company))
        self.assertEqual(result.name, "ACME")
        self.assertEqual(CompanyModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        repository = CompanyRepository()
        res = asyncio.run(repository.select_by_id(doc.id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = CompanyRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid"))

    def test_select_all(self):
        CompanyModel(**self._build_company("ACME").model_dump()).save()
        CompanyModel(**self._build_company("Beta").model_dump()).save()
        repository = CompanyRepository()
        res = asyncio.run(repository.select_all())
        self.assertEqual(len(res), 2)

    def test_update_company(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        repository = CompanyRepository()
        updated = asyncio.run(
            repository.update(doc.id, {"name": "New ACME"})
        )
        self.assertEqual(updated.name, "New ACME")

    def test_update_company_not_found(self):
        repository = CompanyRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.update("invalid", {"name": "New"}))

    def test_delete_company(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        repository = CompanyRepository()
        result = asyncio.run(repository.delete_by_id(doc.id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(CompanyModel.objects(id=doc.id).first().is_active)

    def test_delete_company_not_found(self):
        repository = CompanyRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid"))

    def test_add_member(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        repository = CompanyRepository()
        member = CompanyMember(user_id="usr1", role="owner")
        updated = asyncio.run(repository.add_member(doc.id, member))
        self.assertEqual(len(updated.members), 1)
        self.assertEqual(updated.members[0].user_id, "usr1")
        self.assertEqual(updated.members[0].role, "owner")

    def test_add_member_unique_user(self):
        c1 = CompanyModel(**self._build_company("One").model_dump())
        c1.save()
        c2 = CompanyModel(**self._build_company("Two").model_dump())
        c2.save()
        repository = CompanyRepository()
        member = CompanyMember(user_id="usr1", role="owner")
        asyncio.run(repository.add_member(c1.id, member))
        with self.assertRaises(UnprocessableEntity):
            asyncio.run(repository.add_member(c2.id, member))

    def test_select_by_user(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        repository = CompanyRepository()
        member = CompanyMember(user_id="usr1", role="owner")
        asyncio.run(repository.add_member(doc.id, member))
        res = asyncio.run(repository.select_by_user("usr1"))
        self.assertEqual(res.id, doc.id)

    def test_select_by_user_not_found(self):
        repository = CompanyRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_user("usr1"))


if __name__ == "__main__":
    unittest.main()
