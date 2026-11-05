from functools import cache
from typing import Literal

from pydantic import (
    PostgresDsn,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: Literal["dev", "test", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    exchanges: list[str] = ["binance", "bybit", "okx"]
    kafka_bootstrap: str = "localhost:9092"
    postgres_dsn: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username="marketlens",
        password="marketlens",
        host="localhost",
        port=5432,
        path="marketlens",
    )
    llm_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_prefix="MARKETLENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@cache
def get_settings() -> Settings:
    return Settings()
