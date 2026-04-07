from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "async-content-summarizer"
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/context-summarizer"
    redis_url: str = "redis://redis:6379/0"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 20.0


settings = Settings()

