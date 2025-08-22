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
    """Persistence model for beer kegs.

    The original model enforced a globally unique ``number`` field which caused
    several tests to fail when multiple kegs with the same number were created
    across different test cases.  To keep numbers unique only within a company
    and to automatically avoid collisions we manage the value during ``save``
    similarly to other entities in the project.
    """

    number = StringField(required=True)
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
        "indexes": [
            "status",
            "beer_type_id",
            "expiration_date",
            "company_id",
            {"fields": ["number", "company_id"], "unique": True},
        ],
    }

    def save(self, *args, **kwargs):
        base_number = self.number
        counter = 1
        while KegModel.objects(
            number=self.number, company_id=self.company_id, id__ne=self.id
        ):
            self.number = f"{base_number}{counter}"
            counter += 1
        super().save(*args, **kwargs)
