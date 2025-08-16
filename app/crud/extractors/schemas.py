from pydantic import Field

from app.core.models.base_schema import GenericModel
from app.core.models.base_model import DatabaseModel


class Extractor(GenericModel):
    brand: str = Field(example="Acme")


class ExtractorInDB(DatabaseModel):
    brand: str = Field(example="Acme")


class UpdateExtractor(GenericModel):
    brand: str | None = Field(default=None, example="Acme")
