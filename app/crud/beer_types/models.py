from decimal import Decimal
from mongoengine import StringField, DecimalField

from app.core.models.base_document import BaseDocument


class BeerTypeModel(BaseDocument):
    name = StringField(required=True)
    producer = StringField()
    abv = DecimalField(precision=2)
    ibu = DecimalField(precision=2)
    description = StringField()
    default_sale_price_per_l = DecimalField(required=True, precision=2)
    company_id = StringField(required=True)

    meta = {
        "collection": "beer_types",
        "indexes": ["name", "company_id"],
    }
