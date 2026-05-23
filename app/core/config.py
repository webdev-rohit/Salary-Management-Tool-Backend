"""Application config loaded from .env via pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API settings. Env vars and .env are loaded automatically."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Salary-Management-Tool-Backend"

    database_url: str = Field(...)
    page_size_max: int = Field(default=100)

    secret_key: str = Field(...)
    algorithm: str = Field(default="HS256")
    access_token_valid_time: int = Field(default=60)

settings = Settings()