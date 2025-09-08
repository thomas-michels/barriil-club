from typing import List

from fastapi.encoders import jsonable_encoder
from mongoengine import NotUniqueError
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError, UnprocessableEntity
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import CustomerModel
from .schemas import Customer, CustomerInDB

_logger = get_logger(__name__)


class CustomerRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, customer: Customer, company_id: str) -> CustomerInDB:
        try:
            json = jsonable_encoder(customer.model_dump())
            customer_model = CustomerModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            customer_model.save()
            return CustomerInDB.model_validate(customer_model)
        except NotUniqueError:
            raise UnprocessableEntity(
                message="Customer document should be unique for the company"
            )
        except Exception as error:
            _logger.error(f"Error on create_customer: {str(error)}")
            raise UnprocessableEntity(message="Error on create new customer")

    async def update(
        self, customer_id: str, company_id: str, customer: dict
    ) -> CustomerInDB:
        try:
            customer_model: CustomerModel = CustomerModel.objects(
                id=customer_id, company_id=company_id, is_active=True
            ).first()
            if not customer_model:
                raise NotFoundError(message=f"Customer #{customer_id} not found")

            customer_model.update(**customer)
            customer_model.save()

            return await self.select_by_id(customer_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_customer: {str(error)}")
            raise UnprocessableEntity(message="Error on update customer")

    async def select_by_id(self, id: str, company_id: str) -> CustomerInDB:
        try:
            customer_model: CustomerModel = CustomerModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            return CustomerInDB.model_validate(customer_model)
        except ValidationError:
            raise NotFoundError(message=f"Customer #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"Customer #{id} not found")

    async def select_all(self, company_id: str) -> List[CustomerInDB]:
        try:
            customers: List[CustomerInDB] = []
            for customer_model in CustomerModel.objects(
                company_id=company_id, is_active=True
            ).order_by("name"):
                customers.append(CustomerInDB.model_validate(customer_model))
            return customers
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Customers not found")

    async def delete_by_id(self, id: str, company_id: str) -> CustomerInDB:
        try:
            customer_model: CustomerModel = CustomerModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not customer_model:
                raise NotFoundError(message=f"Customer #{id} not found")
            customer_model.soft_delete()
            customer_model.save()
            return CustomerInDB.model_validate(customer_model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"Customer #{id} not found")
