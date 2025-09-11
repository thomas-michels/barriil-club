from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import decode_jwt
from app.api.composers.company_composite import company_composer
from app.crud.companies.services import CompanyServices
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
        detail="Usuário já pertence a uma empresa",
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
            detail="Usuário não pertence a nenhuma empresa",
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    if any(member.user_id == current_user.user_id for member in company.members):
        return company

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Usuário não é membro desta empresa",
    )


async def require_company_owner(
    company_id: str,
    current_user: UserInDB = Depends(decode_jwt),
    company_services: CompanyServices = Depends(company_composer),
) -> CompanyInDB:
    """Ensure the current user is an owner of the given company."""
    try:
        company = await company_services.search_by_id(id=company_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")

    for member in company.members:
        if member.user_id == current_user.user_id:
            if member.role == "owner":
                return company
            break

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Usuário não é proprietário desta empresa",
    )
