from mongoengine import StringField

from app.core.models.base_document import BaseDocument


class ExtractorModel(BaseDocument):
    brand = StringField(required=True)
    company_id = StringField(required=True)

    meta = {
        "collection": "extractors",
    }
