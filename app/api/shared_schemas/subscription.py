from enum import Enum
from pydantic import Field

from app.core.models.base_schema import GenericModel


class SubscriptionPeriodEnum(str, Enum):
    MONTHLY: str = "MONTHLY"
    ANUALLY: str = "ANUALLY"


class RequestSubscription(GenericModel):
    plan_id: str = Field(example="plan_123")
    period: SubscriptionPeriodEnum = Field(default=SubscriptionPeriodEnum.ANUALLY, example=False)
    organization_id: str= Field(example="org_123")
    allow_additional: bool = Field(default=False, example=False)
    coupon_id: str | None = Field(default=None, example="cou_123")

    def get_sub_months(self) -> int:
        months_quantity = {
            SubscriptionPeriodEnum.MONTHLY: 1,
            SubscriptionPeriodEnum.ANUALLY: 12,
        }

        return months_quantity[self.period]

    def get_label(self) -> str:
        months_label = {
            SubscriptionPeriodEnum.MONTHLY: "Mensal",
            SubscriptionPeriodEnum.ANUALLY: "Anual",
        }

        return months_label[self.period]


class ResponseSubscription(GenericModel):
    invoice_id: str = Field(example="inv_123")
    integration_id: str = Field(example="int_123")
    init_point: str = Field(example="www.mercadopago.com.br")
    email: str = Field(example="email@gmail.com")
