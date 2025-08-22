from mongoengine import DateField, StringField

from app.core.models.base_document import BaseDocument
from .schemas import ExtractionKitStatus, ExtractionKitType


class ExtractionKitModel(BaseDocument):
    type = StringField(required=True, choices=[t.value for t in ExtractionKitType])
    last_calibration_date = DateField()
    status = StringField(required=True, choices=[s.value for s in ExtractionKitStatus])
    notes = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "extraction_kits",
        "indexes": ["status", "type", "company_id"],
    }
