import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "DiaWise AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_MINUTES: int = 60 * 24 * 7

    CORS_ORIGINS: str = "http://localhost:5173"

    # LangSmith tracing for the interview agent — off by default so tests/CI
    # never require network access; see configure_langsmith_tracing().
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str = "diawise-ai"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def psycopg_database_url(self) -> str:
        """The langgraph-checkpoint-postgres saver uses psycopg (v3), not
        asyncpg — DATABASE_URL is an asyncpg DSN for SQLAlchemy, so this
        strips the `+asyncpg` driver qualifier down to a plain postgresql://
        DSN that psycopg accepts.
        """
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def configure_langsmith_tracing() -> None:
    """Push LangSmith settings into the environment variables the LangSmith/
    LangChain SDKs read directly (they don't know about our pydantic
    Settings). No-ops unless both tracing is enabled and a real API key is
    configured, so this is safe to call unconditionally at app startup.
    """
    settings = get_settings()
    if not settings.LANGSMITH_TRACING or not settings.LANGSMITH_API_KEY:
        return
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGSMITH_API_KEY", settings.LANGSMITH_API_KEY)
    os.environ.setdefault("LANGSMITH_PROJECT", settings.LANGSMITH_PROJECT)
