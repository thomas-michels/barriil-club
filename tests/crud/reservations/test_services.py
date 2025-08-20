import asyncio
import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal

import mongomock
from mongoengine import connect, disconnect

from app.core.exceptions import BadRequestError
from app.crud.beer_dispensers.models import BeerDispenserModel
from app.crud.beer_dispensers.schemas import DispenserStatus, Voltage
from app.crud.cylinders.models import CylinderModel
from app.crud.cylinders.repositories import CylinderRepository
from app.crud.cylinders.schemas import CylinderStatus
from app.crud.extractors.models import ExtractorModel
from app.crud.kegs.models import KegModel
from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.schemas import KegStatus
from app.crud.payments.schemas import Payment
from app.crud.pressure_gauges.models import PressureGaugeModel
from app.crud.pressure_gauges.repositories import PressureGaugeRepository
from app.crud.pressure_gauges.schemas import PressureGaugeStatus, PressureGaugeType
from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.schemas import (
    Reservation,
    ReservationStatus,
    UpdateReservation,
)
from app.crud.reservations.services import ReservationServices


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
        self.cyl_repo = CylinderRepository()
        self.services = ReservationServices(
            reservation_repo, self.keg_repo, self.pg_repo, self.cyl_repo
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
            type=PressureGaugeType.SIMPLE.value,
            status=PressureGaugeStatus.ACTIVE.value,
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
        self.extractor = ExtractorModel(brand="Acme", company_id=self.company_id)
        self.extractor.save()

    def tearDown(self) -> None:
        disconnect()

    def test_create_and_complete_reservation(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        res = asyncio.run(self.services.create(reservation, self.company_id))
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
        cyl = CylinderModel.objects(id=self.cylinder.id).first()
        self.assertEqual(cyl.status, CylinderStatus.TO_VERIFY.value)

    def test_create_reservation_conflict(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        asyncio.run(self.services.create(reservation, self.company_id))
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
        new_cylinder = CylinderModel(
            brand="Acme",
            weight_kg=10,
            number="C2",
            status=CylinderStatus.AVAILABLE.value,
            company_id=self.company_id,
        )
        new_cylinder.save()
        reservation2 = Reservation(
            customer_id="cus2",
            address_id="add3",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(new_keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(new_cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        with self.assertRaises(BadRequestError):
            asyncio.run(self.services.create(reservation2, self.company_id))

    def test_create_reservation_cylinder_conflict(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        asyncio.run(self.services.create(reservation, self.company_id))
        new_keg = KegModel(
            number="3",
            size_l=50,
            beer_type_id="bty1",
            cost_price_per_l=5.0,
            sale_price_per_l=8.0,
            status=KegStatus.AVAILABLE.value,
            company_id=self.company_id,
        )
        new_keg.save()
        new_dispenser = BeerDispenserModel(
            brand="Acme",
            status=DispenserStatus.ACTIVE.value,
            voltage=Voltage.V110.value,
            company_id=self.company_id,
        )
        new_dispenser.save()
        reservation2 = Reservation(
            customer_id="cus2",
            address_id="add3",
            beer_dispenser_ids=[str(new_dispenser.id)],
            keg_ids=[str(new_keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        with self.assertRaises(BadRequestError):
            asyncio.run(self.services.create(reservation2, self.company_id))

    def test_create_reservation_with_unavailable_cylinder(self):
        self.cylinder.status = CylinderStatus.TO_VERIFY.value
        self.cylinder.save()
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        with self.assertRaises(BadRequestError):
            asyncio.run(self.services.create(reservation, self.company_id))

    def test_create_reservation_with_empty_cylinder(self):
        empty_cyl = CylinderModel(
            brand="Acme",
            weight_kg=0,
            number="C2",
            status=CylinderStatus.AVAILABLE.value,
            company_id=self.company_id,
        )
        empty_cyl.save()
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(empty_cyl.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        with self.assertRaises(BadRequestError):
            asyncio.run(self.services.create(reservation, self.company_id))

    def test_create_reservation_with_unavailable_keg(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        asyncio.run(self.services.create(reservation, self.company_id))
        # second reservation with same keg but no dispenser conflict
        new_dispenser = BeerDispenserModel(
            brand="Acme",
            status=DispenserStatus.ACTIVE.value,
            voltage=Voltage.V110.value,
            company_id=self.company_id,
        )
        new_dispenser.save()
        reservation2 = Reservation(
            customer_id="cus2",
            address_id="add3",
            beer_dispenser_ids=[str(new_dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=3),
            pickup_date=datetime.now() + timedelta(days=4),
            payments=[],
        )
        with self.assertRaises(BadRequestError):
            asyncio.run(self.services.create(reservation2, self.company_id))

    def test_add_update_delete_payment(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        res = asyncio.run(self.services.create(reservation, self.company_id))
        pay = Payment(amount=Decimal("50.00"), method="cash", paid_at=date.today())
        updated = asyncio.run(self.services.add_payment(res.id, self.company_id, pay))
        self.assertEqual(len(updated.payments), 1)
        new_pay = Payment(amount=Decimal("60.00"), method="card", paid_at=date.today())
        updated = asyncio.run(
            self.services.update_payment(res.id, self.company_id, 0, new_pay)
        )
        self.assertEqual(updated.payments[0].amount, Decimal("60.00"))
        updated = asyncio.run(self.services.delete_payment(res.id, self.company_id, 0))
        self.assertEqual(len(updated.payments), 0)

    def test_total_value_with_charges(self):
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("50.00"),
            additional_value=Decimal("10.00"),
            discount=Decimal("20.00"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        res = asyncio.run(self.services.create(reservation, self.company_id))
        self.assertEqual(res.total_value, Decimal("440.00"))

    def test_create_with_multiple_dispensers(self):
        disp2 = BeerDispenserModel(
            brand="Acme2",
            status=DispenserStatus.ACTIVE.value,
            voltage=Voltage.V110.value,
            company_id=self.company_id,
        )
        disp2.save()
        reservation = Reservation(
            customer_id="cus1",
            address_id="add2",
            beer_dispenser_ids=[str(self.dispenser.id), str(disp2.id)],
            keg_ids=[str(self.keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        res = asyncio.run(self.services.create(reservation, self.company_id))
        self.assertEqual(len(res.beer_dispenser_ids), 2)
        new_keg = KegModel(
            number="77",
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
            beer_dispenser_ids=[str(disp2.id)],
            keg_ids=[str(new_keg.id)],
            extractor_ids=[str(self.extractor.id)],
            pressure_gauge_ids=[str(self.pg.id)],
            cylinder_ids=[str(self.cylinder.id)],
            freight_value=Decimal("0"),
            additional_value=Decimal("0"),
            discount=Decimal("0"),
            delivery_date=datetime.now() + timedelta(days=1),
            pickup_date=datetime.now() + timedelta(days=2),
            payments=[],
        )
        with self.assertRaises(BadRequestError):
            asyncio.run(self.services.create(reservation2, self.company_id))


if __name__ == "__main__":
    unittest.main()
