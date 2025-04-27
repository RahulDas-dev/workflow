from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class UploadConfig(BaseSettings):
    MAX_CONTENT_LENGTH: PositiveInt = Field(description="Maximum Upload Size", default=10 * 1024 * 1024 * 1024)  # 1 MB
