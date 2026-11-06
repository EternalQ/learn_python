import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from marketlens.config import Settings, get_settings


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ):
        if key.startswith("MARKETLENS_"):
            monkeypatch.delenv(key)


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_is_cached() -> None:
    assert get_settings() is get_settings()


def test_settings_cache_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = get_settings()
    assert settings.env == "dev"
    monkeypatch.setenv("MARKETLENS_ENV", "prod")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.env == "prod"


def test_defaults() -> None:
    s = Settings()
    assert s.env == "dev"
    assert s.exchanges == ["binance", "bybit", "okx"]
    assert s.llm_api_key is None


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MARKETLENS_ENV", "prod")
    monkeypatch.setenv("MARKETLENS_EXCHANGES", '["binance"]')
    s = Settings()
    assert s.env == "prod"
    assert s.exchanges == ["binance"]


def test_dotenv_file_is_read(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("MARKETLENS_LOG_LEVEL=DEBUG\n", encoding="utf-8")
    assert Settings().log_level == "DEBUG"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("MARKETLENS_ENV", "staging"),
        ("MARKETLENS_LOG_LEVEL", "TRACE"),
        ("MARKETLENS_POSTGRES_PORT", "abc"),
    ],
)
def test_invalid_values_rejected(monkeypatch: pytest.MonkeyPatch, key: str, value: str) -> None:
    monkeypatch.setenv(key, value)
    with pytest.raises(ValidationError):
        Settings()


def test_secret_not_leaked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MARKETLENS_LLM_API_KEY", "sk-test-123")
    s = Settings()
    assert "sk-test-123" not in repr(s)
    assert s.llm_api_key is not None
    assert s.llm_api_key.get_secret_value() == "sk-test-123"


def test_dsn_cred_not_leaked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MARKETLENS_POSTGRES_USER", "s3cret-user")
    monkeypatch.setenv("MARKETLENS_POSTGRES_PASS", "s3cret-pass")
    s = Settings()

    assert "s3cret-user" not in s.model_dump_json()
    assert "s3cret-user" not in repr(s)
    assert "s3cret-user" in str(s.postgres_dsn)

    assert "s3cret-pass" not in s.model_dump_json()
    assert "s3cret-pass" not in repr(s)
    assert "s3cret-pass" in str(s.postgres_dsn)


def test_empty_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MARKETLENS_POSTGRES_PORT", "")
    monkeypatch.setenv("MARKETLENS_LLM_API_KEY", "")
    s = Settings()

    assert s.postgres_port == 5432
    assert s.llm_api_key is None
