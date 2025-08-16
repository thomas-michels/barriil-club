from pydantic import Field, BaseModel

from app.crud.shared_schemas.roles import RoleEnum


class RequestRole(BaseModel):
    role: RoleEnum = Field(example=RoleEnum.MEMBER)
