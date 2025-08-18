import asyncio
import unittest

import mongomock
from mongoengine import connect, disconnect

from app.crud.cylinders.repositories import CylinderRepository
from app.crud.cylinders.services import CylinderServices
from app.crud.cylinders.schemas import Cylinder, UpdateCylinder, CylinderStatus
from app.crud.cylinders.models import CylinderModel
from app.core.exceptions import NotFoundError


class TestCylinderServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        CylinderModel.drop_collection()
        self.repository = CylinderRepository()
        self.services = CylinderServices(self.repository)

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
        result = asyncio.run(
            self.services.create(self._build_cylinder(), company_id="com1")
        )
        self.assertEqual(result.brand, "Acme")

    def test_search_by_id(self):
        doc = CylinderModel(
            **self._build_cylinder().model_dump(), company_id="com1"
        )
        doc.save()
        res = asyncio.run(self.services.search_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_all(self):
        CylinderModel(
            **self._build_cylinder().model_dump(), company_id="com1"
        ).save()
        res = asyncio.run(self.services.search_all("com1"))
        self.assertEqual(len(res), 1)

    def test_update_cylinder(self):
        doc = CylinderModel(
            **self._build_cylinder().model_dump(), company_id="com1"
        )
        doc.save()
        updated = asyncio.run(
            self.services.update(
                doc.id, doc.company_id, UpdateCylinder(brand="New")
            )
        )
        self.assertEqual(updated.brand, "New")

    def test_delete_cylinder(self):
        doc = CylinderModel(
            **self._build_cylinder().model_dump(), company_id="com1"
        )
        doc.save()
        res = asyncio.run(self.services.delete_by_id(doc.id, doc.company_id))
        self.assertEqual(res.id, doc.id)

    def test_search_by_id_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.search_by_id("invalid", "com1"))

    def test_delete_not_found(self):
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.delete_by_id("invalid", "com1"))


if __name__ == "__main__":
    unittest.main()
