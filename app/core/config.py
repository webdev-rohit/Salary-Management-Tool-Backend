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

settings = Settings()