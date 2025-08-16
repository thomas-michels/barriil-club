from pydantic import ConfigDict, Field
from app.core.models.base_schema import GenericModel
from app.core.utils.utc_datetime import UTCDateTime, UTCDateTimeType


class User(GenericModel):
    email: str = Field(example="test@test.com")
    name: str = Field(example="test")
    nickname: str = Field(example="test")
    picture: str | None = Field(default=None, example="http://localhost")


class UserInDB(User):
    user_id: str = Field(example="id-123")
    user_metadata: dict | None = Field(default=None)
    app_metadata: dict | None = Field(default={})
    last_login: UTCDateTimeType | None = Field(default=None, example=str(UTCDateTime.now()))
    created_at: UTCDateTimeType = Field(example=str(UTCDateTime.now()))
    updated_at: UTCDateTimeType = Field(example=str(UTCDateTime.now()))

    model_config = ConfigDict(extra="allow", from_attributes=True)


class UpdateUser(GenericModel):
    blocked: bool | None = Field(default=None, example=True)
    email: str | None = Field(default=None, example="test@test.com")
    name: str | None = Field(default=None, example="test")
    nickname: str | None = Field(default=None, example="test")
    picture: str | None = Field(default=None, example="http://localhost")
    user_metadata: dict | None = Field(default=None)
    app_metadata: dict | None = Field(default=None)
