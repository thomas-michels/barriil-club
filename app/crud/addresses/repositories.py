from typing import List

from fastapi.encoders import jsonable_encoder
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import AddressModel
from .schemas import Address, AddressInDB

_logger = get_logger(__name__)


class AddressRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, address: Address, company_id: str) -> AddressInDB:
        try:
            json = jsonable_encoder(address.model_dump())
            address_model = AddressModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                company_id=company_id,
                **json,
            )
            address_model.save()
            return AddressInDB.model_validate(address_model)
        except Exception as error:
            _logger.error(f"Error on create_address: {str(error)}")
            raise NotFoundError(message="Error on create new address")

    async def update(self, address_id: str, company_id: str, address: dict) -> AddressInDB:
        try:
            address_model: AddressModel = AddressModel.objects(
                id=address_id, company_id=company_id, is_active=True
            ).first()
            if not address_model:
                raise NotFoundError(message=f"Address #{address_id} not found")

            address_model.update(**address)
            address_model.save()

            return await self.select_by_id(address_id, company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_address: {str(error)}")
            raise NotFoundError(message="Error on update address")

    async def select_active_by_id(self, id: str) -> AddressInDB:
        try:
            address_model: AddressModel = AddressModel.objects(
                id=id, is_active=True
            ).first()
            return AddressInDB.model_validate(address_model)
        except ValidationError:
            raise NotFoundError(message=f"Address #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_active_by_id: {str(error)}")
            raise NotFoundError(message=f"Address #{id} not found")

    async def select_by_id(self, id: str, company_id: str) -> AddressInDB:
        try:
            address_model: AddressModel = AddressModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()

            return AddressInDB.model_validate(address_model)
        except ValidationError:
            raise NotFoundError(message=f"Address #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"Address #{id} not found")

    async def select_all(self, company_id: str) -> List[AddressInDB]:
        try:
            addresses: List[AddressInDB] = []
            for address_model in AddressModel.objects(
                company_id=company_id, is_active=True
            ).order_by("city"):
                addresses.append(AddressInDB.model_validate(address_model))
            return addresses
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Addresses not found")

    async def delete_by_id(self, id: str, company_id: str) -> AddressInDB:
        try:
            address_model: AddressModel = AddressModel.objects(
                id=id, company_id=company_id, is_active=True
            ).first()
            if not address_model:
                raise NotFoundError(message=f"Address #{id} not found")
            address_model.soft_delete()
            address_model.save()
            return AddressInDB.model_validate(address_model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"Address #{id} not found")

    async def select_by_zip_code(
        self, zip_code: str, company_id: str, *, raise_404: bool = True
    ) -> AddressInDB | None:
        try:
            sanitized = zip_code.replace("-", "")
            formatted = (
                f"{sanitized[:5]}-{sanitized[5:]}" if len(sanitized) > 5 else sanitized
            )
            address_model: AddressModel | None = AddressModel.objects(
                postal_code__in=[zip_code, sanitized, formatted],
                company_id=company_id,
                is_active=True,
            ).first()
            if not address_model and raise_404:
                raise NotFoundError(
                    message=f"Address with zip code {zip_code} not found"
                )
            if not address_model:
                return None
            return AddressInDB.model_validate(address_model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on select_by_zip_code: {str(error)}")
            raise NotFoundError(
                message=f"Address with zip code {zip_code} not found"
            )
