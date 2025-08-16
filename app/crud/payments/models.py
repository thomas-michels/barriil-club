from mongoengine import EmbeddedDocument, DecimalField, StringField, DateField


class PaymentModel(EmbeddedDocument):
    amount = DecimalField(required=True, precision=2)
    method = StringField(required=True)
    paid_at = DateField(required=True)
