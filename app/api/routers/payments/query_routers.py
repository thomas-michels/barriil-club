from fastapi import APIRouter, Depends

from app.api.composers.payment_composite import payment_composer
from app.api.dependencies import build_response, require_user_company
from app.crud.payments.services import PaymentServices
from app.crud.payments.schemas import PaymentStatus
from app.crud.companies.schemas import CompanyInDB
from .schemas import PaymentListResponse

router = APIRouter(tags=["Payments"])


@router.get(
    "/payments",
    responses={200: {"model": PaymentListResponse}},
)
async def get_payments(
    status: PaymentStatus | None = None,
    services: PaymentServices = Depends(payment_composer),
    company: CompanyInDB = Depends(require_user_company),
):
    payments = await services.search_all(company_id=str(company.id), status=status)
    return build_response(
        status_code=200,
        message="Payments found with success",
        data=payments or [],
    )
