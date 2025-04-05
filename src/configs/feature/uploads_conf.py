from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class UploadConfig(BaseSettings):
    UPLOADS_DEFAULT_DEST: str = Field(description="Path to the propeller model", default="")
    ALLOWED_EXTENSIONS: list[str] = Field(
        description="Allowed extensions for the uploaded files", default_factory=lambda: ["pdf", "PDF", "png", "PNG"]
    )
    CLEANUP_TEMP_FILES: bool = Field(description="Cleanup temporary files", default=True)

    @field_validator("UPLOADS_DEFAULT_DEST", mode="before")
    @classmethod
    def validate_directory1(cls, value: str) -> str:
        if not Path(value).is_dir():
            raise ValueError(f"{value} is not a valid directory")
        return value
