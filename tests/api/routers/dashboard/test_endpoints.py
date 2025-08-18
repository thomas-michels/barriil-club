import asyncio
import unittest
from datetime import timedelta
from decimal import Decimal

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.dashboard import dashboard_router
from app.api.routers.exception_handlers import not_found_error_404
from app.api.dependencies.company import require_user_company
from app.api.composers.dashboard_composite import dashboard_composer
from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.services import ReservationServices
from app.crud.reservations.schemas import Reservation, ReservationStatus
from app.crud.dashboard.services import DashboardServices
from app.crud.companies.schemas import CompanyInDB
from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.services import KegServices
from app.crud.kegs.schemas import Keg, KegStatus
from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.crud.cylinders.repositories import CylinderRepository
from app.crud.extractors.models import ExtractorModel
from app.crud.beer_dispensers.models import BeerDispenserModel
from app.crud.pressure_gauges.models import PressureGaugeModel
from app.crud.cylinders.models import CylinderModel
from app.crud.beer_dispensers.schemas import DispenserStatus, Voltage
from app.crud.pressure_gauges.schemas import PressureGaugeStatus, PressureGaugeType
from app.crud.cylinders.schemas import CylinderStatus
from app.core.utils.utc_datetime import UTCDateTime
from app.core.exceptions import NotFoundError


class TestDashboardEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.fixed_now = UTCDateTime(2024, 1, 1, 0, 0, 0)
        self._orig_now = UTCDateTime.now
        UTCDateTime.now = classmethod(lambda cls, tz=None: self.fixed_now)

        self.reservation_repo = ReservationRepository()
        self.keg_repo = KegRepository()
        self.pg_repo = PressureGaugeRepository()
        self.cyl_repo = CylinderRepository()
        self.reservation_services = ReservationServices(
            self.reservation_repo, self.keg_repo, self.pg_repo, self.cyl_repo
        )
        self.keg_services = KegServices(self.keg_repo)
        self.dashboard_services = DashboardServices(
            self.reservation_services, self.keg_services
        )

        self.app = FastAPI()
        self.app.include_router(dashboard_router, prefix="/api")
        self.app.add_exception_handler(NotFoundError, not_found_error_404)

        self.company = CompanyInDB(
            id="com1",
            name="ACME",
            address_id="add1",
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
            members=[],
            created_at=self.fixed_now,
            updated_at=self.fixed_now,
        )

        async def override_require_user_company():
            return self.company

        async def override_dashboard_composer():
            return self.dashboard_services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[dashboard_composer] = override_dashboard_composer

        self.client = TestClient(self.app)

        keg1 = Keg(
            number="1",
            size_l=50,
            beer_type_id="bty1",
            cost_price_per_l=Decimal("1"),
            sale_price_per_l=Decimal("2"),
            status=KegStatus.AVAILABLE,
        )
        keg2 = Keg(
            number="2",
            size_l=40,
            beer_type_id="bty1",
            cost_price_per_l=Decimal("3"),
            sale_price_per_l=Decimal("5"),
            status=KegStatus.AVAILABLE,
        )
        self.keg1 = asyncio.run(self.keg_repo.create(keg1, self.company.id))
        self.keg2 = asyncio.run(self.keg_repo.create(keg2, self.company.id))
        self.disp1 = BeerDispenserModel(
            brand="Acme",
            status=DispenserStatus.ACTIVE.value,
            voltage=Voltage.V110.value,
            company_id=self.company.id,
        )
        self.disp1.save()
        self.disp2 = BeerDispenserModel(
            brand="Acme",
            status=DispenserStatus.ACTIVE.value,
            voltage=Voltage.V110.value,
            company_id=self.company.id,
        )
        self.disp2.save()
        self.pg_model = PressureGaugeModel(
            brand="Acme",
            type=PressureGaugeType.ANALOG.value,
            status=PressureGaugeStatus.ACTIVE.value,
            company_id=self.company.id,
        )
        self.pg_model.save()
        self.cyl_model = CylinderModel(
            brand="Acme",
            weight_kg=10,
            number="C1",
            status=CylinderStatus.AVAILABLE.value,
            company_id=self.company.id,
        )
        self.cyl_model.save()
        self.ext_model = ExtractorModel(brand="Acme", company_id=self.company.id)
        self.ext_model.save()

        res1 = Reservation(
            customer_id="cus1",
            address_id="add1",
            beer_dispenser_ids=[str(self.disp1.id)],
            keg_ids=[str(self.keg1.id)],
            extractor_ids=[str(self.ext_model.id)],
            pressure_gauge_ids=[str(self.pg_model.id)],
            cylinder_ids=[str(self.cyl_model.id)],
            delivery_date=self.fixed_now + timedelta(days=1),
            pickup_date=self.fixed_now + timedelta(days=2),
            payments=[],
            total_value=Decimal("100.0"),
            status=ReservationStatus.RESERVED,
        )
        res2 = Reservation(
            customer_id="cus2",
            address_id="add1",
            beer_dispenser_ids=[str(self.disp2.id)],
            keg_ids=[str(self.keg2.id)],
            extractor_ids=[str(self.ext_model.id)],
            pressure_gauge_ids=[str(self.pg_model.id)],
            cylinder_ids=[str(self.cyl_model.id)],
            delivery_date=self.fixed_now + timedelta(days=40),
            pickup_date=self.fixed_now + timedelta(days=41),
            payments=[],
            total_value=Decimal("200.0"),
            status=ReservationStatus.RESERVED,
        )
        self.res1 = asyncio.run(self.reservation_repo.create(res1, self.company.id))
        self.res2 = asyncio.run(self.reservation_repo.create(res2, self.company.id))

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        UTCDateTime.now = self._orig_now
        disconnect()

    def test_monthly_revenue(self):
        resp = self.client.get(
            "/api/dashboard/revenue?year=2024"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        jan = next(item for item in data if item["month"] == 1)
        feb = next(item for item in data if item["month"] == 2)
        self.assertEqual(float(jan["revenue"]), 100.0)
        self.assertEqual(float(feb["revenue"]), 200.0)
        self.assertEqual(jan["reservation_count"], 1)
        self.assertEqual(feb["reservation_count"], 1)
        self.assertEqual(jan["liters_sold"], 50)
        self.assertEqual(feb["liters_sold"], 40)
        self.assertEqual(float(jan["cost"]), 50.0)
        self.assertEqual(float(feb["cost"]), 120.0)
        self.assertEqual(float(jan["profit"]), 50.0)
        self.assertEqual(float(feb["profit"]), 80.0)

    def test_upcoming_reservations(self):
        resp = self.client.get(
            "/api/dashboard/upcoming-reservations"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], str(self.res1.id))

    def test_reservation_calendar(self):
        resp = self.client.get(
            "/api/dashboard/calendar?year=2024&month=1"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        day = next(item for item in data if item["day"] == 2)
        self.assertEqual(len(day["reservations"]), 1)
        self.assertEqual(day["reservations"][0]["id"], str(self.res1.id))
