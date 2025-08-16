from datetime import datetime, timezone
from pydantic import ConfigDict, BaseModel


def convert_field_to_camel_case(string: str) -> str:
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )


def convert_datetime_to_realworld(dt: datetime) -> str:
    if str(dt).__contains__("Z"):
        return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

    return dt.replace(tzinfo=timezone.utc)


class GenericModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=convert_field_to_camel_case,
        json_encoders = {datetime: convert_datetime_to_realworld},
        from_attributes=True
    )
