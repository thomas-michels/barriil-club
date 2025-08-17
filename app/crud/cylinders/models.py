from decimal import Decimal
from mongoengine import StringField, DecimalField

from app.core.models.base_document import BaseDocument
from .schemas import CylinderStatus


class CylinderModel(BaseDocument):
    brand = StringField(required=True)
    weight_kg = DecimalField(required=True, precision=2)
    number = StringField(required=True, unique=True)
    status = StringField(required=True, choices=[s.value for s in CylinderStatus])
    notes = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "cylinders",
        "indexes": ["status", "number", "company_id"],
    }
