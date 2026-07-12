"""
Centralized application configuration.

All values are sourced from environment variables (with sane defaults for
local development) via pydantic-settings. This keeps the service
container-friendly and 12-factor compliant.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Service metadata -------------------------------------------------
    service_name: str = "api-gateway"
    log_level: str = "INFO"

    # --- PostgreSQL ---------------------------------------------------------
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "tunisian_legal_assistant"

    # Connection pool sizing
    db_pool_min_size: int = 2
    db_pool_max_size: int = 10
    db_command_timeout: float = 30.0

    # --- JWT ------------------------------------------------------------
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # --- Downstream services ----------------------------------------------
    rag_service_url: str = "http://rag-service:8002"
    rag_service_timeout: float = 60.0

    # --- History window for RAG context -----------------------------------
    rag_history_limit: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we parse the environment only once."""
    return Settings()
