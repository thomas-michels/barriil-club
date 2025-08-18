import asyncio
import unittest
from datetime import timedelta

import mongomock
from mongoengine import connect, disconnect

from app.crud.addresses.models import AddressModel
from app.crud.addresses.repositories import AddressRepository
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import (
    Company,
    UpdateCompany,
    CompanyMember,
    UpdateCompanySubscription,
)
from app.crud.companies.models import CompanyModel, CompanyMember as CompanyMemberModel
from app.core.utils.utc_datetime import UTCDateTime
from app.core.exceptions import NotFoundError, UnprocessableEntity


class TestCompanyServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = CompanyRepository()
        self.address_repository = AddressRepository()
        self.services = CompanyServices(self.repository, self.address_repository)
        address = AddressModel(
            postal_code="12345",
            street="Main",
            number="1",
            district="Center",
            city="City",
            state="ST",
            company_id="dummy",
        )
        address.save()
        self.address_id = address.id

    def tearDown(self) -> None:
        disconnect()

    def _build_company(self, name: str = "ACME", use_address: bool = True) -> Company:
        return Company(
            name=name,
            address_id=self.address_id if use_address else None,
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )

    def test_create_company(self):
        company = self._build_company()
        result = asyncio.run(self.services.create(company))
        self.assertEqual(result.name, "ACME")
        self.assertEqual(CompanyModel.objects.count(), 1)

    def test_create_company_without_address(self):
        company = self._build_company(use_address=False)
        result = asyncio.run(self.services.create(company))
        self.assertEqual(result.address_id, None)

    def test_create_company_invalid_address(self):
        company = Company(
            name="Invalid",
            address_id="invalid",
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.create(company))

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

    def test_update_company_invalid_address(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.update(doc.id, UpdateCompany(address_id="invalid"))
            )

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

    def test_remove_member(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        owner = CompanyMember(user_id="usr1", role="owner")
        member = CompanyMember(user_id="usr2", role="member")
        asyncio.run(self.services.add_member(doc.id, owner))
        asyncio.run(self.services.add_member(doc.id, member))
        updated = asyncio.run(self.services.remove_member(doc.id, "usr2"))
        self.assertEqual(len(updated.members), 1)
        self.assertEqual(updated.members[0].user_id, "usr1")

    def test_remove_member_not_found(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.remove_member(doc.id, "usr1"))

    def test_search_by_user(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.members.append(CompanyMemberModel(user_id="usr1", role="owner"))
        doc.save()
        res = asyncio.run(self.services.search_by_user("usr1"))
        self.assertEqual(res.id, doc.id)

    def test_search_by_user_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_user("usr1"))

    def test_update_subscription(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        new_date = UTCDateTime.now() + timedelta(days=10)
        updated = asyncio.run(
            self.services.update_subscription(
                doc.id, UpdateCompanySubscription(is_active=False, expires_at=new_date)
            )
        )
        self.assertFalse(updated.subscription.is_active)
        self.assertEqual(updated.subscription.expires_at, new_date)

    def test_get_subscription(self):
        doc = CompanyModel(**self._build_company().model_dump())
        doc.save()
        subscription = asyncio.run(self.services.get_subscription(doc.id))
        self.assertTrue(subscription.is_active)


if __name__ == "__main__":
    unittest.main()
