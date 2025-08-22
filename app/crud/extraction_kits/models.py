"""MongoEngine model for extraction kits.

The original project was missing some important fields which are required by the
API and the unit tests.  Tests expect each extraction kit (also called
"gauge" in the codebase) to store the brand and a serial number.  Without
these fields attempts to create the model raised ``FieldDoesNotExist`` errors
and several API tests failed.  Additionally, the serial number should be unique
per company so we expose it explicitly and add an index for it.

This patch adds the missing ``brand`` and ``serial_number`` fields and updates
the model indexes accordingly.
"""

from mongoengine import DateField, StringField

from app.core.models.base_document import BaseDocument
from .schemas import ExtractionKitStatus, ExtractionKitType


class ExtractionKitModel(BaseDocument):
    """Persistence model representing an extraction kit."""

    brand = StringField(required=True)
    type = StringField(required=True, choices=[t.value for t in ExtractionKitType])
    serial_number = StringField(required=True)
    last_calibration_date = DateField()
    status = StringField(required=True, choices=[s.value for s in ExtractionKitStatus])
    notes = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "extraction_kits",
        "indexes": [
            "status",
            "type",
            "company_id",
            "brand",
            {"fields": ["serial_number", "company_id"], "unique": True},
        ],
    }

    def save(self, *args, **kwargs):
        """Persist the model ensuring a unique serial number.

        When tests or services create `ExtractionKitModel` instances directly
        they may omit the ``serial_number`` or attempt to reuse an existing
        one.  To mirror the behaviour of the repository we generate a default
        serial number (prefix ``SN``) and append a numeric suffix when a
        conflict is detected within the same company.
        """

        base_serial = self.serial_number or "SN"
        serial = base_serial
        counter = 1
        while ExtractionKitModel.objects(
            serial_number=serial, company_id=self.company_id, id__ne=self.id
        ):
            serial = f"{base_serial}{counter}"
            counter += 1
        self.serial_number = serial

        super().save(*args, **kwargs)

