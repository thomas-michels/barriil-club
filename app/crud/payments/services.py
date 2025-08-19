from __future__ import annotations

from decimal import Decimal
from typing import List

from app.crud.reservations.repositories import ReservationRepository
from app.crud.customers.repositories import CustomerRepository
from app.crud.payments.schemas import PaymentWithCustomer, PaymentStatus


class PaymentServices:
    def __init__(
        self,
        reservation_repository: ReservationRepository,
        customer_repository: CustomerRepository,
    ) -> None:
        self.__reservation_repository = reservation_repository
        self.__customer_repository = customer_repository

    async def search_all(
        self, company_id: str, status: PaymentStatus | None = None
    ) -> List[PaymentWithCustomer]:
        reservations = await self.__reservation_repository.select_all(
            company_id=company_id
        )
        result: List[PaymentWithCustomer] = []
        for res in reservations:
            paid_value = sum((p.amount for p in res.payments), Decimal("0"))
            pending_value = res.total_value - paid_value
            current_status = (
                PaymentStatus.PAID if pending_value <= 0 else PaymentStatus.PENDING
            )
            if status and current_status != status:
                continue
            customer = await self.__customer_repository.select_by_id(
                res.customer_id, company_id
            )
            result.append(
                PaymentWithCustomer(
                    reservation_id=res.id,
                    customer=customer,
                    total_value=res.total_value,
                    paid_value=paid_value,
                    pending_value=pending_value,
                    status=current_status,
                )
            )
        return result
