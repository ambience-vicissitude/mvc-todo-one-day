"""Environment-driven settings (12-factor: config lives in the environment, not in code).

Defaults here can be overridden by environment variables supplied by Docker Compose or Kubernetes.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with defaults, overridden by environment variables."""

    # Application environment (development, production, etc.), logging level, database url
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://taskapp:dev_only_password@localhost:5432/taskapp"

    # Database connection pool settings
    # Budget: pods x workers x (pool_size + max_overflow) must stay under Postgres max_connections.
    db_pool_size: int = 3
    db_max_overflow: int = 2

    # model config dict for .env settings
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance."""

    return Settings()
