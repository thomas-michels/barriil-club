from typing import List

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime
from app.crud.payments.models import PaymentModel
from app.crud.payments.schemas import Payment

from .models import ReservationModel
from .schemas import ReservationCreate, ReservationInDB, ReservationStatus

_logger = get_logger(__name__)


class ReservationRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(
        self, reservation: ReservationCreate, company_id: str
    ) -> ReservationInDB:
        try:
            payments = [PaymentModel(**p.model_dump()) for p in reservation.payments]
            json = reservation.model_dump(exclude={"payments"})
            json["status"] = reservation.status.value
            json["delivery_date"] = UTCDateTime.validate_datetime(json["delivery_date"])
            json["pickup_date"] = UTCDateTime.validate_datetime(json["pickup_date"])

            model = ReservationModel(
                **json,
                company_id=company_id,
                payments=payments,
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
            )
            model.save()

            return ReservationInDB.model_validate(model)

        except Exception as error:
            _logger.error(f"Error on create_reservation: {str(error)}")
            raise NotFoundError(message="Error on create reservation")

    async def update(
        self, id: str, company_id: str, reservation: dict
    ) -> ReservationInDB:
        try:
            model: ReservationModel = ReservationModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            if not model:
                raise NotFoundError(message=f"Reservation #{id} not found")

            if reservation.get("payments") is not None:
                reservation["payments"] = [
                    PaymentModel(**p) for p in reservation["payments"]
                ]

            model.update(**reservation)
            model.save()
            model = ReservationModel.objects(id=id, company_id=company_id).first()

            return ReservationInDB.model_validate(model)

        except NotFoundError:
            raise

        except Exception as error:
            _logger.error(f"Error on update_reservation: {str(error)}")
            raise NotFoundError(message="Error on update reservation")

    async def add_payment(
        self, id: str, company_id: str, payment: Payment
    ) -> ReservationInDB:
        try:
            model: ReservationModel = ReservationModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            if not model:
                raise NotFoundError(message=f"Reservation #{id} not found")

            model.payments.append(PaymentModel(**payment.model_dump()))
            model.save()

            return ReservationInDB.model_validate(model)

        except NotFoundError:
            raise

        except Exception as error:
            _logger.error(f"Error on add_payment: {str(error)}")
            raise NotFoundError(message="Error on add payment")

    async def update_payment(
        self, id: str, company_id: str, index: int, payment: Payment
    ) -> ReservationInDB:
        try:
            model: ReservationModel = ReservationModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            if not model:
                raise NotFoundError(message=f"Reservation #{id} not found")

            if index < 0 or index >= len(model.payments):
                raise NotFoundError(message=f"Payment #{index} not found")

            model.payments[index] = PaymentModel(**payment.model_dump())
            model.save()

            return ReservationInDB.model_validate(model)

        except NotFoundError:
            raise

        except Exception as error:
            _logger.error(f"Error on update_payment: {str(error)}")
            raise NotFoundError(message="Error on update payment")

    async def delete_payment(
        self, id: str, company_id: str, index: int
    ) -> ReservationInDB:
        try:
            model: ReservationModel = ReservationModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            if not model:
                raise NotFoundError(message=f"Reservation #{id} not found")

            if index < 0 or index >= len(model.payments):
                raise NotFoundError(message=f"Payment #{index} not found")

            model.payments.pop(index)
            model.save()

            return ReservationInDB.model_validate(model)

        except NotFoundError:
            raise

        except Exception as error:
            _logger.error(f"Error on delete_payment: {str(error)}")
            raise NotFoundError(message="Error on delete payment")

    async def find_beer_dispenser_conflict(
        self,
        company_id: str,
        beer_dispenser_ids: List[str],
        delivery_date: UTCDateTime,
        pickup_date: UTCDateTime,
    ) -> ReservationInDB | None:
        try:
            start = UTCDateTime.validate_datetime(delivery_date)
            end = UTCDateTime.validate_datetime(pickup_date)
            model = ReservationModel.objects(
                beer_dispenser_ids__in=beer_dispenser_ids,
                company_id=company_id,
                is_active=True,
                status__ne=ReservationStatus.COMPLETED.value,
                delivery_date__lte=end,
                pickup_date__gte=start,
            ).first()

            return ReservationInDB.model_validate(model) if model else None

        except Exception as error:
            _logger.error(f"Error on find_beer_dispenser_conflict: {str(error)}")
            raise NotFoundError(message="Error on find beer dispenser conflict")

    async def find_cylinder_conflict(
        self,
        company_id: str,
        cylinder_ids: List[str],
        delivery_date: UTCDateTime,
        pickup_date: UTCDateTime,
    ) -> ReservationInDB | None:
        try:
            start = UTCDateTime.validate_datetime(delivery_date)
            end = UTCDateTime.validate_datetime(pickup_date)
            model = ReservationModel.objects(
                cylinder_ids__in=cylinder_ids,
                company_id=company_id,
                is_active=True,
                status__ne=ReservationStatus.COMPLETED.value,
                delivery_date__lte=end,
                pickup_date__gte=start,
            ).first()

            return ReservationInDB.model_validate(model) if model else None

        except Exception as error:
            _logger.error(f"Error on find_cylinder_conflict: {str(error)}")
            raise NotFoundError(message="Error on find cylinder conflict")

    async def find_extractor_conflict(
        self,
        company_id: str,
        extractor_ids: List[str],
        delivery_date: UTCDateTime,
        pickup_date: UTCDateTime,
    ) -> ReservationInDB | None:
        try:
            start = UTCDateTime.validate_datetime(delivery_date)
            end = UTCDateTime.validate_datetime(pickup_date)
            model = ReservationModel.objects(
                extractor_ids__in=extractor_ids,
                company_id=company_id,
                is_active=True,
                status__ne=ReservationStatus.COMPLETED.value,
                delivery_date__lte=end,
                pickup_date__gte=start,
            ).first()

            return ReservationInDB.model_validate(model) if model else None

        except Exception as error:
            _logger.error(f"Error on find_extractor_conflict: {str(error)}")
            raise NotFoundError(message="Error on find extractor conflict")

    async def find_extraction_kit_conflict(
        self,
        company_id: str,
        extraction_kit_ids: List[str],
        delivery_date: UTCDateTime,
        pickup_date: UTCDateTime,
    ) -> ReservationInDB | None:
        try:
            start = UTCDateTime.validate_datetime(delivery_date)
            end = UTCDateTime.validate_datetime(pickup_date)
            model = ReservationModel.objects(
                extraction_kit_ids__in=extraction_kit_ids,
                company_id=company_id,
                is_active=True,
                status__ne=ReservationStatus.COMPLETED.value,
                delivery_date__lte=end,
                pickup_date__gte=start,
            ).first()

            return ReservationInDB.model_validate(model) if model else None

        except Exception as error:
            _logger.error(f"Error on find_extraction_kit_conflict: {str(error)}")
            raise NotFoundError(message="Error on find Extraction kit conflict")

    async def find_active_by_beer_dispenser_id(
        self, company_id: str, dispenser_id: str
    ) -> ReservationInDB | None:
        try:
            now = UTCDateTime.now()
            model = ReservationModel.objects(
                beer_dispenser_ids=dispenser_id,
                company_id=company_id,
                is_active=True,
                status__ne=ReservationStatus.COMPLETED.value,
                delivery_date__lte=now,
                pickup_date__gte=now,
            ).first()

            return ReservationInDB.model_validate(model) if model else None

        except Exception as error:
            _logger.error(f"Error on find_active_by_beer_dispenser_id: {str(error)}")
            raise NotFoundError(message="Error on find reservation by beer dispenser")

    def _auto_update_status(self, model: ReservationModel) -> None:
        # ``ReservationModel`` stores datetimes without timezone information,
        # while :class:`UTCDateTime.now` returns timezone-aware values.  Direct
        # comparisons between them raise ``TypeError`` complaining about naive
        # vs offset-aware datetimes.  We normalise both dates to ``UTCDateTime``
        # before comparison to keep everything in UTC.
        now = UTCDateTime.now()
        delivery_date = UTCDateTime.validate_datetime(model.delivery_date)
        pickup_date = UTCDateTime.validate_datetime(model.pickup_date)

        changed = False
        if model.status == ReservationStatus.RESERVED.value and now >= delivery_date:
            model.status = ReservationStatus.TO_DELIVER.value
            changed = True
        if (
            model.status
            in [ReservationStatus.TO_DELIVER.value, ReservationStatus.DELIVERED.value]
            and now >= pickup_date
        ):
            model.status = ReservationStatus.TO_PICKUP.value
            changed = True
        if changed:
            model.save()

    async def select_by_id(self, id: str, company_id: str) -> ReservationInDB:
        try:
            model: ReservationModel = ReservationModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            if not model:
                raise NotFoundError(message=f"Reservation #{id} not found")

            self._auto_update_status(model)
            return ReservationInDB.model_validate(model)

        except NotFoundError:
            raise

        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"Reservation #{id} not found")

    async def select_all(
        self,
        company_id: str,
        start_date: UTCDateTime | None = None,
        end_date: UTCDateTime | None = None,
        status: str | None = None,
    ) -> List[ReservationInDB]:
        try:
            query = ReservationModel.objects(company_id=company_id, is_active=True)

            if start_date:
                start = UTCDateTime.validate_datetime(start_date)
                query = query.filter(delivery_date__gte=start)

            if end_date:
                end = UTCDateTime.validate_datetime(end_date)
                query = query.filter(pickup_date__lte=end)

            if status:
                query = query.filter(status=status)

            reservations: List[ReservationInDB] = []

            for model in query.order_by("delivery_date"):
                self._auto_update_status(model)
                reservations.append(ReservationInDB.model_validate(model))

            return reservations

        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Reservations not found")

    async def delete_by_id(self, id: str, company_id: str) -> ReservationInDB:
        try:
            model: ReservationModel = ReservationModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            if not model:
                raise NotFoundError(message=f"Reservation #{id} not found")

            model.soft_delete()
            model.save()
            return ReservationInDB.model_validate(model)

        except NotFoundError:
            raise

        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"Reservation #{id} not found")
