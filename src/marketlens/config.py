from functools import cache
from typing import Literal

from pydantic import (
    PostgresDsn,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Settings(BaseSettings):
    env: Literal["dev", "test", "prod"] = "dev"
    log_level: LogLevel = "INFO"
    exchanges: list[str] = ["binance", "bybit", "okx"]
    kafka_bootstrap: str = "localhost:9092"
    llm_api_key: SecretStr | None = None

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: SecretStr = SecretStr("marketlens")
    postgres_pass: SecretStr = SecretStr("marketlens")
    postgres_db: str = "marketlens"

    @property
    def postgres_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user.get_secret_value(),
            password=self.postgres_pass.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    model_config = SettingsConfigDict(
        env_prefix="MARKETLENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


@cache
def get_settings() -> Settings:
    return Settings()
