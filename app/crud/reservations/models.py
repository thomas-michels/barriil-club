from mongoengine import (
    StringField,
    ListField,
    EmbeddedDocumentListField,
    DecimalField,
    DateTimeField,
)

from app.core.models.base_document import BaseDocument
from .schemas import ReservationStatus
from app.crud.payments.models import PaymentModel


class ReservationModel(BaseDocument):
    customer_id = StringField(required=True)
    address_id = StringField(required=True)
    beer_dispenser_ids = ListField(StringField())
    keg_ids = ListField(StringField())
    extractor_ids = ListField(StringField())
    pressure_gauge_ids = ListField(StringField())
    cylinder_ids = ListField(StringField())
    freight_value = DecimalField(default=0, precision=2)
    additional_value = DecimalField(default=0, precision=2)
    discount = DecimalField(default=0, precision=2)
    delivery_date = DateTimeField(required=True)
    pickup_date = DateTimeField(required=True)
    payments = EmbeddedDocumentListField(PaymentModel, default=list)
    total_value = DecimalField(required=True, precision=2)
    status = StringField(required=True, choices=[s.value for s in ReservationStatus])
    company_id = StringField(required=True)

    meta = {
        "collection": "reservations",
        "indexes": [
            "customer_id",
            "company_id",
            "delivery_date",
            "pickup_date",
            "beer_dispenser_ids",
        ],
    }
