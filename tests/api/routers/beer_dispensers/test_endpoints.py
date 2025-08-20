import asyncio
import unittest
from datetime import timedelta

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.beer_dispensers import beer_dispenser_router
from app.api.dependencies.company import require_user_company
from app.api.composers.beer_dispenser_composite import beer_dispenser_composer
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.services import CompanyServices
from app.crud.companies.schemas import Company
from app.crud.addresses.repositories import AddressRepository
from app.crud.addresses.models import AddressModel
from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.beer_dispensers.services import BeerDispenserServices
from app.crud.beer_dispensers.schemas import BeerDispenser, DispenserStatus, Voltage
from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.models import ReservationModel
from app.crud.reservations.schemas import ReservationStatus
from app.core.utils.utc_datetime import UTCDateTime
from app.core.exceptions import NotFoundError


class TestBeerDispenserEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.repository = BeerDispenserRepository()
        self.reservation_repository = ReservationRepository()
        self.services = BeerDispenserServices(
            self.repository, self.reservation_repository
        )
        self.app = FastAPI()
        self.app.include_router(beer_dispenser_router, prefix="/api")

        async def override_require_user_company():
            return self.company


        async def override_dispenser_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[beer_dispenser_composer] = (
            override_dispenser_composer
        )
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
        self.address_id = str(seed_address.id)
        company = Company(
            name="ACME",
            address_id=str(seed_address.id),
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )
        self.company = asyncio.run(self.company_services.create(company))

        dispenser = BeerDispenser(
            brand="Acme",
            model="X1",
            serial_number="SN1",
            taps_count=4,
            voltage=Voltage.V110,
            status=DispenserStatus.ACTIVE,
            notes="",
        )
        self.dispenser = asyncio.run(
            self.services.create(dispenser, company_id=str(self.company.id))
        )

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, brand: str = "NewBrand") -> dict:
        return {
            "brand": brand,
            "model": "X2",
            "serialNumber": "SN2",
            "tapsCount": 2,
            "voltage": "110V",
            "status": "ACTIVE",
        }

    def test_create_dispenser_endpoint(self):
        resp = self.client.post("/api/beer-dispensers", json=self._payload("BrandX"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["brand"], "BrandX")

    def test_get_dispenser_by_id(self):
        resp = self.client.get(
            f"/api/beer-dispensers/{self.dispenser.id}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.dispenser.id)

    def test_list_dispensers(self):
        resp = self.client.get("/api/beer-dispensers")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()["data"]), 1)
        self.assertNotIn("reservation_id", resp.json()["data"][0])

    def test_list_dispensers_shows_reservation_id_when_ongoing(self):
        now = UTCDateTime.now()
        reservation = ReservationModel(
            customer_id="cust_1",
            address_id=self.address_id,
            beer_dispenser_ids=[self.dispenser.id],
            keg_ids=["keg_1"],
            extractor_ids=["ext_1"],
            pressure_gauge_ids=["prg_1"],
            cylinder_ids=["cyl_1"],
            freight_value=0,
            additional_value=0,
            discount=0,
            delivery_date=now - timedelta(hours=1),
            pickup_date=now + timedelta(hours=1),
            total_value=100,
            status=ReservationStatus.RESERVED.value,
            company_id=str(self.company.id),
        )
        reservation.save()

        resp = self.client.get("/api/beer-dispensers")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json()["data"][0]["reservation_id"], reservation.id
        )

    def test_list_dispensers_hides_reservation_id_outside_period(self):
        now = UTCDateTime.now()
        reservation = ReservationModel(
            customer_id="cust_1",
            address_id=self.address_id,
            beer_dispenser_ids=[self.dispenser.id],
            keg_ids=["keg_1"],
            extractor_ids=["ext_1"],
            pressure_gauge_ids=["prg_1"],
            cylinder_ids=["cyl_1"],
            freight_value=0,
            additional_value=0,
            discount=0,
            delivery_date=now - timedelta(days=2),
            pickup_date=now - timedelta(days=1),
            total_value=100,
            status=ReservationStatus.DELIVERED.value,
            company_id=str(self.company.id),
        )
        reservation.save()

        resp = self.client.get("/api/beer-dispensers")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("reservation_id", resp.json()["data"][0])

    def test_list_dispensers_hides_reservation_id_when_completed(self):
        now = UTCDateTime.now()
        reservation = ReservationModel(
            customer_id="cust_1",
            address_id=self.address_id,
            beer_dispenser_ids=[self.dispenser.id],
            keg_ids=["keg_1"],
            extractor_ids=["ext_1"],
            pressure_gauge_ids=["prg_1"],
            cylinder_ids=["cyl_1"],
            freight_value=0,
            additional_value=0,
            discount=0,
            delivery_date=now - timedelta(hours=1),
            pickup_date=now + timedelta(hours=1),
            total_value=100,
            status=ReservationStatus.COMPLETED.value,
            company_id=str(self.company.id),
        )
        reservation.save()

        resp = self.client.get("/api/beer-dispensers")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("reservation_id", resp.json()["data"][0])

    def test_update_dispenser_endpoint(self):
        resp = self.client.put(
            f"/api/beer-dispensers/{self.dispenser.id}",
            json={"brand": "Updated"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["brand"], "Updated")

    def test_delete_dispenser_endpoint(self):
        resp = self.client.delete(
            f"/api/beer-dispensers/{self.dispenser.id}"
        )
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(NotFoundError):
            asyncio.run(
                self.services.search_by_id(self.dispenser.id, str(self.company.id))
            )

    def test_create_dispenser_returns_400_when_not_created(self):
        async def fake_create(dispenser, company_id):
            return None

        self.services.create = fake_create
        resp = self.client.post("/api/beer-dispensers", json=self._payload("Fail"))
        self.assertEqual(resp.status_code, 400)

    def test_update_dispenser_returns_400_when_not_updated(self):
        async def fake_update(id, company_id, dispenser):
            return None

        self.services.update = fake_update
        resp = self.client.put(
            f"/api/beer-dispensers/{self.dispenser.id}",
            json={"brand": "Fail"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_delete_dispenser_returns_400_when_not_deleted(self):
        async def fake_delete(id, company_id):
            return None

        self.services.delete_by_id = fake_delete
        resp = self.client.delete(
            f"/api/beer-dispensers/{self.dispenser.id}"
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
