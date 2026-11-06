set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

sync:
    uv sync

fmt:
    uv run ruff format
    uv run ruff check --fix

lint:
    uv run ruff check
    uv run ruff format --check

typecheck:
    uv run mypy

test:
    uv run pytest

check: lint typecheck test