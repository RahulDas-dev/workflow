from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class UploadConfig(BaseSettings):
    MAX_CONTENT_LENGTH: PositiveInt = Field(description="Maximum Upload Size", default=104857600)  # 1 MB
    MAX_FORM_MEMORY_SIZE: PositiveInt = Field(description="Maximum Upload Size", default=104857600)
    QUART_SCHEMA_CONVERSION_PREFERENCE: str = Field(
        description="Quart Schema Conversion Preference",
        default="pydantic",
    )  # pydantic or marshmallow
