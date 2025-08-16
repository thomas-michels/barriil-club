import asyncio
import unittest
from datetime import date, timedelta
from decimal import Decimal

import mongomock
from mongoengine import connect, disconnect

from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.services import ReservationServices
from app.crud.reservations.schemas import (
    Reservation,
    UpdateReservation,
    ReservationStatus,
)
from app.crud.kegs.models import KegModel
from app.crud.kegs.schemas import KegStatus
from app.crud.kegs.repositories import KegRepository
from app.crud.beer_dispensers.models import BeerDispenserModel
from app.crud.beer_dispensers.schemas import DispenserStatus, Voltage
from app.crud.pressure_gauges.models import PressureGaugeModel
from app.crud.pressure_gauges.schemas import (
    PressureGaugeStatus,
    PressureGaugeType,
)
from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.core.exceptions import NotFoundError


class TestReservationServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        reservation_repo = ReservationRepository()
        self.keg_repo = KegRepository()
        self.pg_repo = PressureGaugeRepository()
        self.services = ReservationServices(
            reservation_repo, self.keg_repo, self.pg_repo
        )
        self.company_id = "com1"
        self.dispenser = BeerDispenserModel(
            brand="Acme",
            status=DispenserStatus.ACTIVE.value,
            voltage=Voltage.V110.value,
            company_id=self.company_id,
        )
        self.dispenser.save()
        self.keg = KegModel(
            number="1",
            size_l=50,
            beer_type_id="bty1",
            cost_price_per_l=5.0,
            sale_price_per_l=8.0,
            status=KegStatus.AVAILABLE.value,
            company_id=self.company_id,
        )
        self.keg.save()
        self.pg = PressureGaugeModel(
            brand="Acme",
            type=PressureGaugeType.ANALOG.value,
            status=PressureGaugeStatus.ACTIVE.value,
            company_id=self.company_id,
        )
        self.pg.save()

    def tearDown(self) -> None:
        disconnect()

    def test_create_and_complete_reservation(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_id=str(self.dispenser.id),
            keg_ids=[str(self.keg.id)],
            extractor_ids=[],
            pressure_gauge_ids=[str(self.pg.id)],
            delivery_date=date.today() + timedelta(days=1),
            pickup_date=date.today() + timedelta(days=2),
            payments=[],
            company_id=self.company_id,
        )
        res = asyncio.run(self.services.create(reservation))
        self.assertEqual(res.status, ReservationStatus.RESERVED)
        self.assertEqual(res.total_value, Decimal("400.00"))
        updated = asyncio.run(
            self.services.update(
                res.id,
                self.company_id,
                UpdateReservation(status=ReservationStatus.COMPLETED),
            )
        )
        self.assertEqual(updated.status, ReservationStatus.COMPLETED)
        keg = KegModel.objects(id=self.keg.id).first()
        self.assertEqual(keg.status, KegStatus.EMPTY.value)
        pg = PressureGaugeModel.objects(id=self.pg.id).first()
        self.assertEqual(pg.status, PressureGaugeStatus.TO_VERIFY.value)

    def test_create_reservation_conflict(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_id=str(self.dispenser.id),
            keg_ids=[str(self.keg.id)],
            extractor_ids=[],
            pressure_gauge_ids=[str(self.pg.id)],
            delivery_date=date.today() + timedelta(days=1),
            pickup_date=date.today() + timedelta(days=2),
            payments=[],
            company_id=self.company_id,
        )
        asyncio.run(self.services.create(reservation))
        new_keg = KegModel(
            number="2",
            size_l=50,
            beer_type_id="bty1",
            cost_price_per_l=5.0,
            sale_price_per_l=8.0,
            status=KegStatus.AVAILABLE.value,
            company_id=self.company_id,
        )
        new_keg.save()
        reservation2 = Reservation(
            customer_id="cus2",
            address_id="add3",
            beer_dispenser_id=str(self.dispenser.id),
            keg_ids=[str(new_keg.id)],
            extractor_ids=[],
            pressure_gauge_ids=[str(self.pg.id)],
            delivery_date=date.today() + timedelta(days=1),
            pickup_date=date.today() + timedelta(days=2),
            payments=[],
            company_id=self.company_id,
        )
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.create(reservation2))

    def test_create_reservation_with_unavailable_keg(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_id=str(self.dispenser.id),
            keg_ids=[str(self.keg.id)],
            extractor_ids=[],
            pressure_gauge_ids=[str(self.pg.id)],
            delivery_date=date.today() + timedelta(days=1),
            pickup_date=date.today() + timedelta(days=2),
            payments=[],
            company_id=self.company_id,
        )
        asyncio.run(self.services.create(reservation))
        # second reservation with same keg but no dispenser conflict
        reservation2 = Reservation(
            customer_id="cus2",
            address_id="add3",
            beer_dispenser_id=None,
            keg_ids=[str(self.keg.id)],
            extractor_ids=[],
            pressure_gauge_ids=[str(self.pg.id)],
            delivery_date=date.today() + timedelta(days=3),
            pickup_date=date.today() + timedelta(days=4),
            payments=[],
            company_id=self.company_id,
        )
        with self.assertRaises(NotFoundError):
            asyncio.run(self.services.create(reservation2))


if __name__ == "__main__":
    unittest.main()
