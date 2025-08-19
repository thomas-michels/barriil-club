import unittest
from datetime import datetime, date
from decimal import Decimal

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.routers.payments import payment_router
from app.api.dependencies.company import require_user_company
from app.api.composers.payment_composite import payment_composer
from app.crud.companies.schemas import CompanyInDB
from app.crud.payments.services import PaymentServices
from app.crud.payments.schemas import PaymentStatus
from app.crud.reservations.repositories import ReservationRepository
from app.crud.customers.repositories import CustomerRepository
from app.crud.payments.models import PaymentModel
from app.crud.reservations.models import ReservationModel
from app.crud.customers.models import CustomerModel
from app.crud.reservations.schemas import ReservationStatus
from app.core.utils.utc_datetime import UTCDateTime


class TestPaymentEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.reservation_repo = ReservationRepository()
        self.customer_repo = CustomerRepository()
        self.services = PaymentServices(self.reservation_repo, self.customer_repo)

        self.app = FastAPI()
        self.app.include_router(payment_router, prefix="/api")

        self.company = CompanyInDB(
            id="com1",
            name="ACME",
            address_id=None,
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
            created_at=UTCDateTime.now(),
            updated_at=UTCDateTime.now(),
        )

        async def override_require_user_company():
            return self.company

        async def override_payment_composer():
            return self.services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[payment_composer] = override_payment_composer

        self.client = TestClient(self.app)

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
        self.app.dependency_overrides = {}
        disconnect()

    def test_get_payments(self):
        resp = self.client.get("/api/payments")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]), 2)

    def test_get_payments_filtered_paid(self):
        resp = self.client.get(
            "/api/payments", params={"status": PaymentStatus.PAID.value}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]), 1)
        self.assertEqual(resp.json()["data"][0]["status"], PaymentStatus.PAID)

    def test_get_payments_filtered_pending(self):
        resp = self.client.get(
            "/api/payments", params={"status": PaymentStatus.PENDING.value}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]), 1)
        self.assertEqual(resp.json()["data"][0]["status"], PaymentStatus.PENDING)


if __name__ == "__main__":
    unittest.main()
