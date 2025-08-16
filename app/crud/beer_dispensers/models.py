from mongoengine import StringField, IntField

from app.core.models.base_document import BaseDocument
from .schemas import DispenserStatus, Voltage


class BeerDispenserModel(BaseDocument):
    brand = StringField(required=True)
    model = StringField()
    serial_number = StringField()
    taps_count = IntField()
    voltage = StringField(choices=[v.value for v in Voltage])
    status = StringField(required=True, choices=[s.value for s in DispenserStatus])
    notes = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "beer_dispensers",
        "indexes": ["status", "brand", "serial_number", "company_id"],
    }
