import asyncio
import unittest
from datetime import date, datetime, timedelta

import mongomock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from app.api.composers.reservation_composite import reservation_composer
from app.api.dependencies.company import require_user_company
from app.api.routers.exception_handlers import generic_error_400, not_found_error_404
from app.api.routers.reservations import reservation_router
from app.core.exceptions import BadRequestError, NotFoundError
from app.crud.addresses.models import AddressModel
from app.crud.addresses.repositories import AddressRepository
from app.crud.beer_dispensers.repositories import BeerDispenserRepository
from app.crud.beer_dispensers.schemas import BeerDispenser, DispenserStatus, Voltage
from app.crud.beer_dispensers.services import BeerDispenserServices
from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.schemas import Company
from app.crud.companies.services import CompanyServices
from app.crud.cylinders.repositories import CylinderRepository
from app.crud.cylinders.schemas import Cylinder, CylinderStatus, UpdateCylinder
from app.crud.cylinders.services import CylinderServices
from app.crud.extraction_kits.repositories import (
    ExtractionKitRepository
)
from app.crud.extraction_kits.schemas import (
    ExtractionKit,
    ExtractionKitStatus,
    ExtractionKitType,
)
from app.crud.extraction_kits.services import (
    ExtractionKitServices,
)
from app.crud.kegs.repositories import KegRepository
from app.crud.kegs.schemas import Keg, KegStatus, UpdateKeg
from app.crud.kegs.services import KegServices
from app.crud.reservations.repositories import ReservationRepository
from app.crud.reservations.services import ReservationServices


class TestReservationEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        self.company_repo = CompanyRepository()
        self.address_repo = AddressRepository()
        self.company_services = CompanyServices(self.company_repo, self.address_repo)
        self.keg_repo = KegRepository()
        self.pg_repo = ExtractionKitRepository()
        self.cyl_repo = CylinderRepository()
        self.reservation_repo = ReservationRepository()
        self.reservation_services = ReservationServices(
            self.reservation_repo, self.keg_repo, self.pg_repo, self.cyl_repo
        )
        self.keg_services = KegServices(self.keg_repo)
        self.dispenser_repo = BeerDispenserRepository()
        self.dispenser_services = BeerDispenserServices(self.dispenser_repo)
        self.extraction_kit_services = ExtractionKitServices(self.pg_repo)
        self.cylinder_services = CylinderServices(self.cyl_repo)

        self.app = FastAPI()
        self.app.include_router(reservation_router, prefix="/api")
        self.app.add_exception_handler(NotFoundError, not_found_error_404)
        self.app.add_exception_handler(BadRequestError, generic_error_400)

        async def override_require_user_company():
            return self.company

        async def override_reservation_composer():
            return self.reservation_services

        self.app.dependency_overrides[require_user_company] = (
            override_require_user_company
        )
        self.app.dependency_overrides[reservation_composer] = (
            override_reservation_composer
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
        company = Company(
            name="ACME",
            address_id=str(seed_address.id),
            phone_number="9999-9999",
            ddd="11",
            email="info@acme.com",
        )
        self.company = asyncio.run(self.company_services.create(company))

        reservation_address = AddressModel(
            postal_code="12345",
            street="Main",
            number="1",
            district="Center",
            city="City",
            state="ST",
            company_id=str(self.company.id),
        )
        reservation_address.save()
        self.reservation_address_id = str(reservation_address.id)

        self.dispenser = asyncio.run(
            self.dispenser_services.create(
                BeerDispenser(
                    brand="Acme",
                    model="X1",
                    serial_number="SN1",
                    taps_count=4,
                    voltage=Voltage.V110,
                    status=DispenserStatus.ACTIVE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )

        self.keg = asyncio.run(
            self.keg_services.create(
                Keg(
                    number="1",
                    size_l=50,
                    beer_type_id="bty1",
                    cost_price_per_l=5.0,
                    sale_price_per_l=8.0,
                    lot="L1",
                    expiration_date=None,
                    current_volume_l=25.0,
                    status=KegStatus.AVAILABLE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )

        self.extraction_kit = asyncio.run(
            self.extraction_kit_services.create(
                ExtractionKit(
                    brand="Acme",
                    type=ExtractionKitType.SIMPLE,
                    status=ExtractionKitStatus.ACTIVE,
                ),
                company_id=str(self.company.id),
            )
        )

        self.cylinder = asyncio.run(
            self.cylinder_services.create(
                Cylinder(
                    brand="Acme",
                    weight_kg=10,
                    number="C1",
                    status=CylinderStatus.AVAILABLE,
                ),
                company_id=str(self.company.id),
            )
        )

    def tearDown(self) -> None:
        self.app.dependency_overrides = {}
        disconnect()

    def _payload(self, delivery: datetime | None = None) -> dict:
        delivery = delivery or (datetime.now() + timedelta(days=1))
        pickup = delivery + timedelta(days=1)
        return {
            "customerId": "cus1",
            "addressId": self.reservation_address_id,
            "beerDispenserIds": [self.dispenser.id],
            "kegIds": [self.keg.id],
            "extractorIds": [self.extractor.id],
            "ExtractionKitIds": [self.extraction_kit.id],
            "cylinderIds": [self.cylinder.id],
            "freightValue": 0.0,
            "additionalValue": 0.0,
            "discount": 0.0,
            "deliveryDate": delivery.isoformat(),
            "pickupDate": pickup.isoformat(),
            "payments": [
                {"amount": 50.0, "method": "cash", "paidAt": str(date.today())}
            ],
        }

    def test_create_reservation(self):
        resp = self.client.post("/api/reservations", json=self._payload())
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["status"], "RESERVED")
        self.assertEqual(resp.json()["data"]["total_cost"], 250.0)
        keg = asyncio.run(
            self.keg_services.search_by_id(self.keg.id, str(self.company.id))
        )
        self.assertEqual(keg.status, KegStatus.IN_USE)

    def test_create_reservation_multiple_dispensers(self):
        new_disp = asyncio.run(
            self.dispenser_services.create(
                BeerDispenser(
                    brand="Acme",
                    model="X2",
                    serial_number="SN2",
                    taps_count=4,
                    voltage=Voltage.V110,
                    status=DispenserStatus.ACTIVE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        payload = self._payload()
        payload["beerDispenserIds"] = [self.dispenser.id, new_disp.id]
        resp = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(resp.json()["data"]["beer_dispenser_ids"]), 2)

    def test_create_reservation_total_value_with_charges(self):
        payload = self._payload()
        payload["freightValue"] = 50.0
        payload["additionalValue"] = 10.0
        payload["discount"] = 20.0
        resp = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["data"]["total_value"], 440.0)
        self.assertEqual(resp.json()["data"]["total_cost"], 250.0)

    def test_create_reservation_missing_extractor(self):
        payload = self._payload()
        payload["extractorIds"] = []
        resp = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp.status_code, 422)

    def test_create_reservation_dispenser_conflict(self):
        resp1 = self.client.post("/api/reservations", json=self._payload())
        self.assertEqual(resp1.status_code, 201)
        # create a new keg to avoid keg conflict
        new_keg = asyncio.run(
            self.keg_services.create(
                Keg(
                    number="2",
                    size_l=50,
                    beer_type_id="bty1",
                    cost_price_per_l=5.0,
                    sale_price_per_l=8.0,
                    lot="L1",
                    expiration_date=None,
                    current_volume_l=25.0,
                    status=KegStatus.AVAILABLE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_cyl = asyncio.run(
            self.cylinder_services.create(
                Cylinder(
                    brand="Acme",
                    weight_kg=10,
                    number="C2",
                    status=CylinderStatus.AVAILABLE,
                ),
                company_id=str(self.company.id),
            )
        )
        new_pg = asyncio.run(
            self.extraction_kit_services.create(
                ExtractionKit(
                    brand="Acme",
                    type=ExtractionKitType.SIMPLE,
                    status=ExtractionKitStatus.ACTIVE,
                ),
                company_id=str(self.company.id),
            )
        )
        payload = self._payload()
        payload["kegIds"] = [new_keg.id]
        payload["cylinderIds"] = [new_cyl.id]
        payload["ExtractionKitIds"] = [new_pg.id]
        resp2 = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp2.status_code, 400)

    def test_create_reservation_with_empty_keg(self):
        # mark keg as empty
        asyncio.run(
            self.keg_services.update(
                self.keg.id,
                str(self.company.id),
                UpdateKeg(status=KegStatus.EMPTY),
            )
        )
        resp = self.client.post("/api/reservations", json=self._payload())
        self.assertEqual(resp.status_code, 400)

    def test_create_reservation_cylinder_conflict(self):
        resp1 = self.client.post("/api/reservations", json=self._payload())
        self.assertEqual(resp1.status_code, 201)
        new_keg = asyncio.run(
            self.keg_services.create(
                Keg(
                    number="3",
                    size_l=50,
                    beer_type_id="bty1",
                    cost_price_per_l=5.0,
                    sale_price_per_l=8.0,
                    lot="L1",
                    expiration_date=None,
                    current_volume_l=25.0,
                    status=KegStatus.AVAILABLE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_dispenser = asyncio.run(
            self.dispenser_services.create(
                BeerDispenser(
                    brand="Acme",
                    model="X2",
                    serial_number="SN2",
                    taps_count=4,
                    voltage=Voltage.V110,
                    status=DispenserStatus.ACTIVE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_pg = asyncio.run(
            self.extraction_kit_services.create(
                ExtractionKit(
                    brand="Acme",
                    type=ExtractionKitType.SIMPLE,
                    status=ExtractionKitStatus.ACTIVE,
                ),
                company_id=str(self.company.id),
            )
        )
        payload = self._payload()
        payload["kegIds"] = [new_keg.id]
        payload["beerDispenserIds"] = [new_dispenser.id]
        payload["ExtractionKitIds"] = [new_pg.id]
        resp2 = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp2.status_code, 400)

    def test_create_reservation_extractor_conflict(self):
        resp1 = self.client.post("/api/reservations", json=self._payload())
        self.assertEqual(resp1.status_code, 201)
        new_keg = asyncio.run(
            self.keg_services.create(
                Keg(
                    number="4",
                    size_l=50,
                    beer_type_id="bty1",
                    cost_price_per_l=5.0,
                    sale_price_per_l=8.0,
                    lot="L1",
                    expiration_date=None,
                    current_volume_l=25.0,
                    status=KegStatus.AVAILABLE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_dispenser = asyncio.run(
            self.dispenser_services.create(
                BeerDispenser(
                    brand="Acme",
                    model="X3",
                    serial_number="SN3",
                    taps_count=4,
                    voltage=Voltage.V110,
                    status=DispenserStatus.ACTIVE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_pg = asyncio.run(
            self.extraction_kit_services.create(
                ExtractionKit(
                    brand="Acme",
                    type=ExtractionKitType.SIMPLE,
                    status=ExtractionKitStatus.ACTIVE,
                ),
                company_id=str(self.company.id),
            )
        )
        new_cyl = asyncio.run(
            self.cylinder_services.create(
                Cylinder(
                    brand="Acme",
                    weight_kg=10,
                    number="C3",
                    status=CylinderStatus.AVAILABLE,
                ),
                company_id=str(self.company.id),
            )
        )
        payload = self._payload()
        payload["kegIds"] = [new_keg.id]
        payload["beerDispenserIds"] = [new_dispenser.id]
        payload["ExtractionKitIds"] = [new_pg.id]
        payload["cylinderIds"] = [new_cyl.id]
        # use same extractor to trigger conflict
        resp2 = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp2.status_code, 400)

    def test_create_reservation_extraction_kit_conflict(self):
        resp1 = self.client.post("/api/reservations", json=self._payload())
        self.assertEqual(resp1.status_code, 201)
        new_keg = asyncio.run(
            self.keg_services.create(
                Keg(
                    number="5",
                    size_l=50,
                    beer_type_id="bty1",
                    cost_price_per_l=5.0,
                    sale_price_per_l=8.0,
                    lot="L1",
                    expiration_date=None,
                    current_volume_l=25.0,
                    status=KegStatus.AVAILABLE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_dispenser = asyncio.run(
            self.dispenser_services.create(
                BeerDispenser(
                    brand="Acme",
                    model="X4",
                    serial_number="SN4",
                    taps_count=4,
                    voltage=Voltage.V110,
                    status=DispenserStatus.ACTIVE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_cyl = asyncio.run(
            self.cylinder_services.create(
                Cylinder(
                    brand="Acme",
                    weight_kg=10,
                    number="C4",
                    status=CylinderStatus.AVAILABLE,
                ),
                company_id=str(self.company.id),
            )
        )
        payload = self._payload()
        payload["kegIds"] = [new_keg.id]
        payload["beerDispenserIds"] = [new_dispenser.id]
        payload["cylinderIds"] = [new_cyl.id]
        # use same Extraction kit to trigger conflict
        resp2 = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp2.status_code, 400)

    def test_create_reservation_with_unavailable_cylinder(self):
        asyncio.run(
            self.cylinder_services.update(
                self.cylinder.id,
                str(self.company.id),
                UpdateCylinder(status=CylinderStatus.TO_VERIFY),
            )
        )
        resp = self.client.post("/api/reservations", json=self._payload())
        self.assertEqual(resp.status_code, 400)

    def test_create_reservation_with_empty_cylinder(self):
        empty_cyl = asyncio.run(
            self.cylinder_services.create(
                Cylinder(
                    brand="Acme",
                    weight_kg=0,
                    number="C2",
                    status=CylinderStatus.AVAILABLE,
                ),
                company_id=str(self.company.id),
            )
        )
        payload = self._payload()
        payload["cylinderIds"] = [empty_cyl.id]
        resp = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_complete_reservation_updates_items(self):
        resp = self.client.post("/api/reservations", json=self._payload())
        res_id = resp.json()["data"]["id"]
        resp2 = self.client.put(
            f"/api/reservations/{res_id}",
            json={"status": "COMPLETED"},
        )
        self.assertEqual(resp2.status_code, 200)
        keg = asyncio.run(
            self.keg_services.search_by_id(self.keg.id, str(self.company.id))
        )
        self.assertEqual(keg.status, KegStatus.EMPTY)
        pg = asyncio.run(
            self.extraction_kit_services.search_by_id(
                self.extraction_kit.id, str(self.company.id)
            )
        )
        self.assertEqual(pg.status, ExtractionKitStatus.TO_VERIFY)
        cyl = asyncio.run(
            self.cylinder_services.search_by_id(self.cylinder.id, str(self.company.id))
        )
        self.assertEqual(cyl.status, CylinderStatus.TO_VERIFY)
        dispenser = asyncio.run(
            self.dispenser_services.search_by_id(
                self.dispenser.id, str(self.company.id)
            )
        )
        self.assertEqual(dispenser.status, DispenserStatus.ACTIVE)

    def test_create_reservation_rejects_status_field(self):
        payload = self._payload()
        payload["status"] = "COMPLETED"
        resp = self.client.post("/api/reservations", json=payload)
        self.assertEqual(resp.status_code, 422)

    def test_payment_endpoints(self):
        resp = self.client.post("/api/reservations", json=self._payload())
        res_id = resp.json()["data"]["id"]
        pay_payload = {
            "amount": 25.0,
            "method": "card",
            "paidAt": str(date.today()),
        }
        resp_add = self.client.post(
            f"/api/reservations/{res_id}/payments",
            json=pay_payload,
        )
        self.assertEqual(resp_add.status_code, 200)
        self.assertEqual(len(resp_add.json()["data"]["payments"]), 2)
        resp_update = self.client.put(
            f"/api/reservations/{res_id}/payments/1",
            json={"amount": 60.0, "method": "card", "paidAt": str(date.today())},
        )
        self.assertEqual(resp_update.status_code, 200)
        self.assertEqual(resp_update.json()["data"]["payments"][1]["amount"], 60.0)
        resp_delete = self.client.delete(
            f"/api/reservations/{res_id}/payments/0",
        )
        self.assertEqual(resp_delete.status_code, 200)
        self.assertEqual(len(resp_delete.json()["data"]["payments"]), 1)

    def test_list_reservations_with_filters(self):
        resp1 = self.client.post("/api/reservations", json=self._payload())
        res_id1 = resp1.json()["data"]["id"]
        # second reservation far in future with different keg to avoid conflict
        future_delivery = datetime.now() + timedelta(days=10)
        new_keg = asyncio.run(
            self.keg_services.create(
                Keg(
                    number="99",
                    size_l=50,
                    beer_type_id="bty1",
                    cost_price_per_l=5.0,
                    sale_price_per_l=8.0,
                    lot="L2",
                    expiration_date=None,
                    current_volume_l=25.0,
                    status=KegStatus.AVAILABLE,
                    notes="",
                ),
                company_id=str(self.company.id),
            )
        )
        new_cyl = asyncio.run(
            self.cylinder_services.create(
                Cylinder(
                    brand="Acme",
                    weight_kg=10,
                    number="C99",
                    status=CylinderStatus.AVAILABLE,
                ),
                company_id=str(self.company.id),
            )
        )
        payload = self._payload(future_delivery)
        payload["kegIds"] = [new_keg.id]
        payload["cylinderIds"] = [new_cyl.id]
        resp2 = self.client.post("/api/reservations", json=payload)
        res_id2 = resp2.json()["data"]["id"]
        # complete first reservation
        self.client.put(
            f"/api/reservations/{res_id1}",
            json={"status": "COMPLETED"},
        )
        # filter by status
        resp = self.client.get(
            "/api/reservations",
            params={
                "status": "COMPLETED",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]), 1)
        self.assertEqual(resp.json()["data"][0]["id"], res_id1)
        # filter by date range to get second reservation only
        start = future_delivery - timedelta(days=1)
        end = future_delivery + timedelta(days=2)
        resp = self.client.get(
            "/api/reservations",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["data"]), 1)
        self.assertEqual(resp.json()["data"][0]["id"], res_id2)


if __name__ == "__main__":
    unittest.main()
