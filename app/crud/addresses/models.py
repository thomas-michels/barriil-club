from mongoengine import StringField

from app.core.models.base_document import BaseDocument


class AddressModel(BaseDocument):
    postal_code = StringField(required=True)
    street = StringField(required=True)
    number = StringField(required=True)
    complement = StringField()
    district = StringField(required=True)
    city = StringField(required=True)
    state = StringField(required=True)
    reference = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "addresses",
        "indexes": [
            "postal_code",
            "company_id",
            {"fields": ["city", "state"]},
        ],
    }
