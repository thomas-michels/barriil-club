import asyncio
import unittest
from datetime import datetime, date
from decimal import Decimal

import mongomock
from mongoengine import connect, disconnect

from app.crud.payments.services import PaymentServices
from app.crud.payments.schemas import PaymentStatus
from app.crud.reservations.repositories import ReservationRepository
from app.crud.customers.repositories import CustomerRepository
from app.crud.payments.models import PaymentModel
from app.crud.reservations.models import ReservationModel
from app.crud.customers.models import CustomerModel
from app.crud.reservations.schemas import ReservationStatus


class TestPaymentServices(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.reservation_repo = ReservationRepository()
        self.customer_repo = CustomerRepository()
        self.services = PaymentServices(self.reservation_repo, self.customer_repo)

        cust1 = CustomerModel(
            name="John",
            document="10000000019",
            company_id="com1",
        )
        cust1.save()
        cust2 = CustomerModel(
            name="Jane",
            document="10000000108",
            company_id="com1",
        )
        cust2.save()

        ReservationModel(
            customer_id=str(cust1.id),
            address_id="add1",
            beer_dispenser_ids=["bsd1"],
            keg_ids=["keg1"],
            extractor_ids=["ext1"],
            pressure_gauge_ids=["prg1"],
            cylinder_ids=["cyl1"],
            freight_value=0,
            additional_value=0,
            discount=0,
            delivery_date=datetime.now(),
            pickup_date=datetime.now(),
            payments=[
                PaymentModel(amount=Decimal("100.0"), method="cash", paid_at=date.today())
            ],
            total_value=Decimal("100.0"),
            status=ReservationStatus.COMPLETED.value,
            company_id="com1",
        ).save()

        ReservationModel(
            customer_id=str(cust2.id),
            address_id="add1",
            beer_dispenser_ids=["bsd1"],
            keg_ids=["keg1"],
            extractor_ids=["ext1"],
            pressure_gauge_ids=["prg1"],
            cylinder_ids=["cyl1"],
            freight_value=0,
            additional_value=0,
            discount=0,
            delivery_date=datetime.now(),
            pickup_date=datetime.now(),
            payments=[
                PaymentModel(amount=Decimal("50.0"), method="cash", paid_at=date.today())
            ],
            total_value=Decimal("100.0"),
            status=ReservationStatus.DELIVERED.value,
            company_id="com1",
        ).save()

    def tearDown(self) -> None:
        disconnect()

    def test_search_all(self):
        payments = asyncio.run(self.services.search_all(company_id="com1"))
        self.assertEqual(len(payments), 2)
        statuses = {p.status for p in payments}
        self.assertIn(PaymentStatus.PAID, statuses)
        self.assertIn(PaymentStatus.PENDING, statuses)

    def test_search_all_filtered_paid(self):
        payments = asyncio.run(
            self.services.search_all(company_id="com1", status=PaymentStatus.PAID)
        )
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].status, PaymentStatus.PAID)

    def test_search_all_filtered_pending(self):
        payments = asyncio.run(
            self.services.search_all(company_id="com1", status=PaymentStatus.PENDING)
        )
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].status, PaymentStatus.PENDING)


if __name__ == "__main__":
    unittest.main()
