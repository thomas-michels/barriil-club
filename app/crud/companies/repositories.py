from typing import List

from app.core.exceptions import NotFoundError, UnprocessableEntity

from .models import CompanyModel, CompanyMember
from .schemas import Company, CompanyInDB, UpdateCompany, CompanyMember as CompanyMemberSchema


class CompanyRepository:
    async def create(self, company: Company) -> CompanyInDB:
        document = CompanyModel(**company.model_dump())
        document.save()
        return CompanyInDB.model_validate(document)

    async def select_by_id(self, id: str, raise_404: bool = True) -> CompanyInDB | None:
        document = CompanyModel.objects(id=id, is_active=True).first()
        if document:
            return CompanyInDB.model_validate(document)
        if raise_404:
            raise NotFoundError(message=f"Company {id} not found")
        return None

    async def select_all(self) -> List[CompanyInDB]:
        documents = CompanyModel.objects(is_active=True).all()
        return [CompanyInDB.model_validate(doc) for doc in documents]

    async def update(self, id: str, company: UpdateCompany) -> CompanyInDB:
        document = CompanyModel.objects(id=id, is_active=True).first()
        if not document:
            raise NotFoundError(message=f"Company {id} not found")
        data = company.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in data.items():
            setattr(document, field, value)
        document.base_update()
        document.save()
        return CompanyInDB.model_validate(document)

    async def delete_by_id(self, id: str) -> bool:
        document = CompanyModel.objects(id=id, is_active=True).first()
        if not document:
            return False
        document.soft_delete()
        document.save()
        return True

    async def add_member(
        self, company_id: str, member: CompanyMemberSchema
    ) -> CompanyInDB:
        if CompanyModel.objects(members__user_id=member.user_id, is_active=True).first():
            raise UnprocessableEntity(
                message=f"User {member.user_id} already has a company"
            )

        company = CompanyModel.objects(id=company_id, is_active=True).first()
        if not company:
            raise NotFoundError(message=f"Company {company_id} not found")

        company.members.append(
            CompanyMember(user_id=member.user_id, role=member.role)
        )
        company.base_update()
        company.save()
        return CompanyInDB.model_validate(company)
