from mongoengine import StringField

from app.core.models.base_document import BaseDocument


class CompanyModel(BaseDocument):
    name = StringField(required=True)
    address_line1 = StringField(required=True)
    address_line2 = StringField()
    phone_number = StringField(required=True)
    ddd = StringField(required=True)
    email = StringField(required=True)
