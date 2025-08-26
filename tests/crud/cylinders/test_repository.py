import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.cylinders.repositories import CylinderRepository
from app.crud.cylinders.models import CylinderModel
from app.crud.cylinders.schemas import Cylinder, CylinderStatus
from app.core.exceptions import NotFoundError


class TestCylinderRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        CylinderModel.drop_collection()

    def tearDown(self) -> None:
        disconnect()

    def _build_cylinder(self, brand: str = "Acme", number: str = "CY1") -> Cylinder:
        return Cylinder(
            brand=brand,
            weight_kg=10.5,
            number=number,
            status=CylinderStatus.AVAILABLE,
            notes="",
        )

    def test_create_cylinder(self):
        repository = CylinderRepository()
        cylinder = self._build_cylinder()
        result = asyncio.run(repository.create(cylinder, company_id="com1"))
        self.assertEqual(result.brand, "Acme")
        self.assertEqual(CylinderModel.objects.count(), 1)

    def test_select_by_id_found(self):
        doc = CylinderModel(
            **self._build_cylinder().model_dump(), company_id="com1"
        )
        doc.save()
        repository = CylinderRepository()
        res = asyncio.run(repository.select_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_select_by_id_not_found(self):
        repository = CylinderRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.select_by_id("invalid", "com1"))

    def test_select_all(self):
        CylinderModel(
            **self._build_cylinder("A", number="CY1").model_dump(), company_id="com1"
        ).save()
        CylinderModel(
            **self._build_cylinder("B", number="CY2").model_dump(), company_id="com1"
        ).save()
        repository = CylinderRepository()
        res = asyncio.run(repository.select_all("com1"))
        self.assertEqual(len(res), 2)

    def test_update_cylinder(self):
        doc = CylinderModel(
            **self._build_cylinder().model_dump(), company_id="com1"
        )
        doc.save()
        repository = CylinderRepository()
        updated = asyncio.run(
            repository.update(doc.id, doc.company_id, {"brand": "New"})
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_cylinder(self):
        doc = CylinderModel(
            **self._build_cylinder().model_dump(), company_id="com1"
        )
        doc.save()
        repository = CylinderRepository()
        result = asyncio.run(repository.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(result.id, doc.id)
        self.assertFalse(CylinderModel.objects(id=doc.id).first().is_active)

    def test_delete_cylinder_not_found(self):
        repository = CylinderRepository()
        with self.assertRaises(NotFoundError):
            asyncio.run(repository.delete_by_id("invalid", "com1"))

    def test_create_cylinder_allows_duplicate_number(self):
        repository = CylinderRepository()
        cylinder = self._build_cylinder()
        first = asyncio.run(repository.create(cylinder, company_id="com1"))
        second = asyncio.run(repository.create(cylinder, company_id="com1"))
        self.assertEqual(first.number, cylinder.number)
        self.assertEqual(second.number, cylinder.number)
        self.assertEqual(
            CylinderModel.objects(number=cylinder.number, is_active=True).count(), 2
        )


if __name__ == "__main__":
    unittest.main()
