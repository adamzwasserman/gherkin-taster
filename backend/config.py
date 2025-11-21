"""
Application Configuration
Environment-based settings using Pydantic
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Linear Configuration
    linear_api_token: str
    linear_org: str
    linear_team: str

    # GitHub Configuration
    github_api_token: str
    github_org: str

    # LLM Configuration (optional)
    llm_api_key: str | None = None
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Application Configuration
    log_level: str = "INFO"
    environment: str = "development"

    # Session Configuration
    session_ttl: int = 86400  # 24 hours
    edit_lock_ttl: int = 1800  # 30 minutes

    # Email Configuration (optional)
    email_smtp_host: str | None = None
    email_smtp_port: int = 587
    email_smtp_user: str | None = None
    email_smtp_password: str | None = None
    email_from_address: str | None = None

    # Webhook Configuration (optional)
    automation_webhook_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
