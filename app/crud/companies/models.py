from datetime import timedelta

from mongoengine import (
    StringField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
    BooleanField,
    DateTimeField,
)

from app.core.models.base_document import BaseDocument
from app.core.utils.utc_datetime import UTCDateTime


class CompanyMember(EmbeddedDocument):
    user_id = StringField(required=True)
    role = StringField(required=True, choices=("owner", "member"))


class CompanySubscription(EmbeddedDocument):
    is_active = BooleanField(default=True)
    expires_at = DateTimeField(
        default=lambda: UTCDateTime.now() + timedelta(days=7)
    )


class CompanyModel(BaseDocument):
    name = StringField(required=True)
    address_id = StringField()
    phone_number = StringField(required=True)
    ddd = StringField(required=True)
    email = StringField(required=True)
    members = ListField(EmbeddedDocumentField(CompanyMember))
    subscription = EmbeddedDocumentField(
        CompanySubscription, default=CompanySubscription
    )

    meta = {
        "collection": "companies",
    }
