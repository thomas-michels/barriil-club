from mongoengine import StringField, DateField

from app.core.models.base_document import BaseDocument
from .schemas import PressureGaugeType, PressureGaugeStatus


class PressureGaugeModel(BaseDocument):
    brand = StringField(required=True)
    type = StringField(required=True, choices=[t.value for t in PressureGaugeType])
    serial_number = StringField()
    last_calibration_date = DateField()
    status = StringField(required=True, choices=[s.value for s in PressureGaugeStatus])
    notes = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "pressure_gauges",
        "indexes": ["status", "type", "last_calibration_date", "company_id"],
    }
