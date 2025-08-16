from mongoengine import StringField, ValidationError

from app.core.models.base_document import BaseDocument
from app.core.utils.validate_document import validate_cpf, validate_cnpj


class CustomerModel(BaseDocument):
    name = StringField(required=True)
    document = StringField(required=True, unique=True)
    email = StringField()
    mobile = StringField()
    birth_date = StringField()
    address_id = StringField()
    notes = StringField()

    def clean(self):
        if self.document and not (
            validate_cpf(self.document) or validate_cnpj(self.document)
        ):
            raise ValidationError("Invalid document")
