import asyncio
import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal

import mongomock
from mongoengine import connect, disconnect

from app.crud.beer_dispensers.models import BeerDispenserModel
from app.crud.beer_dispensers.schemas import DispenserStatus, Voltage
from app.crud.cylinders.models import CylinderModel
from app.crud.cylinders.schemas import CylinderStatus
from app.crud.extraction_kits.models import ExtractionKitModel
from app.crud.extraction_kits.schemas import ExtractionKitStatus, ExtractionKitType
from app.crud.kegs.models import KegModel
from app.crud.kegs.schemas import KegStatus
from app.crud.payments.schemas import Payment
from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.schemas import ReservationCreate, ReservationStatus


class TestReservationRepository(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.repository = ReservationRepository()
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
        self.pg = ExtractionKitModel(
            brand="Acme",
            type=ExtractionKitType.SIMPLE.value,
            status=ExtractionKitStatus.ACTIVE.value,
            company_id=self.company_id,
        )
        self.pg.save()
        self.cylinder = CylinderModel(
            brand="Acme",
            weight_kg=10,
            number="C1",
            status=CylinderStatus.AVAILABLE.value,
            company_id=self.company_id,
        )
        self.cylinder.save()

    def tearDown(self) -> None:
        disconnect()

    def test_create_reservation(self):
        reservation = ReservationCreate(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extraction_kit_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
            total_value=Decimal("400.00"),
            total_cost=Decimal("250.00"),
            status=ReservationStatus.RESERVED,
        )
        res = asyncio.run(self.repository.create(reservation, self.company_id))
        self.assertIsNotNone(res.id)

    def test_add_update_delete_payment(self):
        reservation = ReservationCreate(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extraction_kit_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
            total_value=Decimal("400.00"),
            total_cost=Decimal("250.00"),
            status=ReservationStatus.RESERVED,
        )
        res = asyncio.run(self.repository.create(reservation, self.company_id))
        pay = Payment(amount=Decimal("50.00"), method="cash", paid_at=date.today())
        updated = asyncio.run(self.repository.add_payment(res.id, self.company_id, pay))
        self.assertEqual(len(updated.payments), 1)
        new_pay = Payment(amount=Decimal("60.00"), method="card", paid_at=date.today())
        updated = asyncio.run(
            self.repository.update_payment(res.id, self.company_id, 0, new_pay)
        )
        self.assertEqual(updated.payments[0].amount, Decimal("60.00"))
        updated = asyncio.run(
            self.repository.delete_payment(res.id, self.company_id, 0)
        )
        self.assertEqual(len(updated.payments), 0)

    def test_find_active_by_beer_dispenser_id_within_period(self):
        reservation = ReservationCreate(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extraction_kit_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() - timedelta(hours=1),
            pickup_date=datetime.now() + timedelta(hours=1),
            payments=[],
            total_value=Decimal("400.00"),
            total_cost=Decimal("250.00"),
            status=ReservationStatus.RESERVED,
        )
        res = asyncio.run(self.repository.create(reservation, self.company_id))
        found = asyncio.run(
            self.repository.find_active_by_beer_dispenser_id(
                self.company_id, str(self.dispenser.id)
            )
        )
        self.assertEqual(found.id, res.id)

    def test_find_active_by_beer_dispenser_id_outside_period(self):
        reservation = ReservationCreate(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extraction_kit_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
            total_value=Decimal("400.00"),
            total_cost=Decimal("250.00"),
            status=ReservationStatus.RESERVED,
        )
        asyncio.run(self.repository.create(reservation, self.company_id))
        found = asyncio.run(
            self.repository.find_active_by_beer_dispenser_id(
                self.company_id, str(self.dispenser.id)
            )
        )
        self.assertIsNone(found)

    def test_find_active_by_beer_dispenser_id_completed(self):
        reservation = ReservationCreate(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extraction_kit_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() - timedelta(hours=1),
            pickup_date=datetime.now() + timedelta(hours=1),
            payments=[],
            total_value=Decimal("400.00"),
            total_cost=Decimal("250.00"),
            status=ReservationStatus.COMPLETED,
        )
        asyncio.run(self.repository.create(reservation, self.company_id))
        found = asyncio.run(
            self.repository.find_active_by_beer_dispenser_id(
                self.company_id, str(self.dispenser.id)
            )
        )
        self.assertIsNone(found)


if __name__ == "__main__":
    unittest.main()
