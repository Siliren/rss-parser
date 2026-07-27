"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central config. Values come from .env or defaults below."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./data/media_nlp.db"
    scrape_delay_seconds: int = 2
    user_agent: str = "MediaNLPAnalyzer/1.0 (Educational Project)"
    log_level: str = "INFO"


settings = Settings()
