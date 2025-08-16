from typing import List

from fastapi.encoders import jsonable_encoder
from mongoengine import NotUniqueError
from pydantic_core import ValidationError

from app.core.configs import get_logger
from app.core.exceptions import NotFoundError, UnprocessableEntity
from app.core.repositories.base_repository import Repository
from app.core.utils.utc_datetime import UTCDateTime

from .models import CompanyModel, CompanyMember
from .schemas import (
    Company,
    CompanyInDB,
    UpdateCompany,
    CompanyMember as CompanyMemberSchema,
)

_logger = get_logger(__name__)


class CompanyRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    async def create(self, company: Company) -> CompanyInDB:
        try:
            json = jsonable_encoder(company.model_dump())
            company_model = CompanyModel(
                is_active=True,
                created_at=UTCDateTime.now(),
                updated_at=UTCDateTime.now(),
                **json,
            )
            company_model.name = company_model.name.strip()
            company_model.save()
            return CompanyInDB.model_validate(company_model)
        except NotUniqueError:
            raise UnprocessableEntity(message="Company name should be unique")
        except Exception as error:
            _logger.error(f"Error on create_company: {str(error)}")
            raise UnprocessableEntity(message="Error on create new company")

    async def update(self, company_id: str, company: dict) -> CompanyInDB:
        try:
            company_model: CompanyModel = CompanyModel.objects(
                id=company_id, is_active=True
            ).first()
            if not company_model:
                raise NotFoundError(message=f"Company #{company_id} not found")

            company_model.update(**company)
            company_model.name = company_model.name.strip()
            company_model.save()

            return await self.select_by_id(company_id)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on update_company: {str(error)}")
            raise UnprocessableEntity(message="Error on update company")

    async def select_by_id(self, id: str) -> CompanyInDB:
        try:
            company_model: CompanyModel = CompanyModel.objects(
                id=id, is_active=True
            ).first()

            return CompanyInDB.model_validate(company_model)
        except ValidationError:
            raise NotFoundError(message=f"Company #{id} not found")
        except Exception as error:
            _logger.error(f"Error on select_by_id: {str(error)}")
            raise NotFoundError(message=f"Company #{id} not found")

    async def select_all(self) -> List[CompanyInDB]:
        try:
            companies: List[CompanyInDB] = []
            for company_model in CompanyModel.objects(is_active=True).order_by("name"):
                companies.append(CompanyInDB.model_validate(company_model))
            return companies
        except Exception as error:
            _logger.error(f"Error on select_all: {str(error)}")
            raise NotFoundError(message="Companies not found")

    async def delete_by_id(self, id: str) -> CompanyInDB:
        try:
            company_model: CompanyModel = CompanyModel.objects(
                id=id, is_active=True
            ).first()
            if not company_model:
                raise NotFoundError(message=f"Company #{id} not found")
            company_model.soft_delete()
            company_model.save()
            return CompanyInDB.model_validate(company_model)
        except NotFoundError:
            raise
        except Exception as error:
            _logger.error(f"Error on delete_by_id: {str(error)}")
            raise NotFoundError(message=f"Company #{id} not found")

    async def add_member(
        self, company_id: str, member: CompanyMemberSchema
    ) -> CompanyInDB:
        try:
            if CompanyModel.objects(
                members__user_id=member.user_id, is_active=True
            ).first():
                raise UnprocessableEntity(
                    message=f"User {member.user_id} already has a company"
                )

            company = CompanyModel.objects(id=company_id, is_active=True).first()

            company.members.append(
                CompanyMember(user_id=member.user_id, role=member.role)
            )
            company.base_update()
            company.save()
            return CompanyInDB.model_validate(company)
        except UnprocessableEntity:
            raise
        except Exception as error:
            _logger.error(f"Error on add_member: {str(error)}")
            raise NotFoundError(message=f"Company {company_id} not found")
