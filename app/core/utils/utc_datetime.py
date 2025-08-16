from datetime import datetime
from typing import Annotated
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema
from pydantic_core import core_schema
import pytz


class UTCDateTime(datetime):
    def __new__(cls, *args, **kwargs):
        if ('tzinfo' in kwargs and kwargs['tzinfo'] is not None) or len(args) == 8:
            temp_dt = datetime(*args, **kwargs)

            utc_dt = temp_dt.astimezone(pytz.UTC)

            return super().__new__(cls, utc_dt.year, utc_dt.month, utc_dt.day,
                                 utc_dt.hour, utc_dt.minute, utc_dt.second,
                                 utc_dt.microsecond, tzinfo=pytz.UTC)

        return super().__new__(cls, *args, **kwargs, tzinfo=pytz.UTC)

    def __str__(self):
        return f"{self.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"

    def timestamp(self) -> int:
        return int(super().timestamp())

    @classmethod
    def now(cls, tz=None):
        now_utc = datetime.now(pytz.UTC)
        return cls(now_utc.year, now_utc.month,
                  now_utc.day, now_utc.hour,
                  now_utc.minute, now_utc.second,
                  now_utc.microsecond)

    @classmethod
    def validate_datetime(cls, v, *args):
        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v)

            except ValueError:
                dt = datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%fZ')

            if dt.tzinfo:
                dt = dt.astimezone(pytz.UTC)

            else:
                dt = pytz.UTC.localize(dt)

            return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)

        elif isinstance(v, datetime):
            if v.tzinfo:
                v = v.astimezone(pytz.UTC)

            else:
                v = pytz.UTC.localize(v)

            return cls(v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond)
        raise ValueError("Invalid datetime format")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        python_schema = core_schema.no_info_plain_validator_function(cls.validate_datetime)

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance),
                return_schema=core_schema.str_schema()
            )
        )


UTCDateTimeType = Annotated[
    UTCDateTime,
    BeforeValidator(UTCDateTime.validate_datetime),
    PlainSerializer(lambda x: x, return_type=datetime),
    WithJsonSchema({"type": "string", "format": "date-time"}, mode="serialization"),
]
