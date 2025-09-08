from mongoengine import StringField, ValidationError
from mongoengine import ListField

from app.core.models.base_document import BaseDocument
from app.core.utils.validate_document import validate_cpf, validate_cnpj


class CustomerModel(BaseDocument):
    name = StringField(required=True)
    document = StringField(required=True)
    email = StringField()
    mobile = StringField()
    birth_date = StringField()
    address_ids = ListField(StringField())
    notes = StringField()
    company_id = StringField(required=True)

    meta = {
        "collection": "customers",
        "indexes": [
            "company_id",
            {"fields": ["document", "company_id"], "unique": True},
        ],
    }

    def clean(self):
        if self.document and not (
            validate_cpf(self.document) or validate_cnpj(self.document)
        ):
            raise ValidationError("Invalid document")
        if self.address_ids and len(self.address_ids) > 5:
            raise ValidationError("A customer can have at most 5 addresses")
