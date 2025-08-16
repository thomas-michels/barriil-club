from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import decode_jwt
from app.api.composers.company_composite import company_composer
from app.crud.companies import CompanyServices
from app.crud.users.schemas import UserInDB
from app.crud.companies.schemas import CompanyInDB
from app.core.exceptions import NotFoundError


async def ensure_user_without_company(
    current_user: UserInDB = Depends(decode_jwt),
    company_services: CompanyServices = Depends(company_composer),
) -> UserInDB:
    """Allow access only if the user is not member of any company."""
    try:
        await company_services.search_by_user(user_id=current_user.user_id)
    except NotFoundError:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already belongs to a company",
    )


async def require_user_company(
    current_user: UserInDB = Depends(decode_jwt),
    company_services: CompanyServices = Depends(company_composer),
) -> CompanyInDB:
    """Return the company the current user belongs to."""
    try:
        return await company_services.search_by_user(user_id=current_user.user_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any company",
        )


async def require_company_member(
    company_id: str,
    current_user: UserInDB = Depends(decode_jwt),
    company_services: CompanyServices = Depends(company_composer),
) -> CompanyInDB:
    """Ensure the current user is member of the given company."""
    try:
        company = await company_services.search_by_id(id=company_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    if any(member.user_id == current_user.user_id for member in company.members):
        return company

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not member of this company",
    )
