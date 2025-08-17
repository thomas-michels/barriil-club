from mongoengine import (
    StringField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
)

from app.core.models.base_document import BaseDocument


class CompanyMember(EmbeddedDocument):
    user_id = StringField(required=True)
    role = StringField(required=True, choices=("owner", "member"))


class CompanyModel(BaseDocument):
    name = StringField(required=True)
    address_id = StringField()
    phone_number = StringField(required=True)
    ddd = StringField(required=True)
    email = StringField(required=True)
    members = ListField(EmbeddedDocumentField(CompanyMember))

    meta = {
        "collection": "companies",
    }
