import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from marketlens.config import Settings


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for key in list(os.environ):
        if key.startswith("MARKETLENS_"):
            monkeypatch.delenv(key)


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
        ("MARKETLENS_POSTGRES_DSN", "mysql://u:p@localhost/db"),
    ],
)
def test_invalid_values_rejected(
    monkeypatch: pytest.MonkeyPatch, key: str, value: str
) -> None:
    monkeypatch.setenv(key, value)
    with pytest.raises(ValidationError):
        Settings()


def test_secret_not_leaked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MARKETLENS_LLM_API_KEY", "sk-test-123")
    s = Settings()
    assert "sk-test-123" not in repr(s)
    assert s.llm_api_key is not None
    assert s.llm_api_key.get_secret_value() == "sk-test-123"
