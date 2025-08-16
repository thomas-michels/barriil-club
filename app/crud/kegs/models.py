from decimal import Decimal
from mongoengine import (
    StringField,
    DecimalField,
    IntField,
    DateField,
)

from app.core.models.base_document import BaseDocument
from .schemas import KegStatus


class KegModel(BaseDocument):
    number = StringField(required=True, unique=True)
    size_l = IntField(required=True)
    beer_type_id = StringField(required=True)
    cost_price_per_l = DecimalField(required=True, precision=2)
    sale_price_per_l = DecimalField(precision=2)
    lot = StringField()
    expiration_date = DateField()
    current_volume_l = DecimalField(precision=2)
    status = StringField(required=True, choices=[status.value for status in KegStatus])
    notes = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "kegs",
        "indexes": ["status", "beer_type_id", "expiration_date", "company_id"],
    }
