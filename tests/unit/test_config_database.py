"""Database path configuration added on top of the Prompt 0 settings."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config import DEFAULT_DATABASE_PATH, ROOT_DIR, Settings, load_settings


def test_database_path_defaults_when_unset() -> None:
    settings = load_settings({"APP_ENV": "test", "LOG_LEVEL": "INFO"})
    assert settings.database_path == DEFAULT_DATABASE_PATH
    assert Path(settings.database_file) == ROOT_DIR / DEFAULT_DATABASE_PATH


def test_database_path_comes_from_environment() -> None:
    settings = load_settings({"APP_ENV": "test", "DATABASE_PATH": ":memory:"})
    assert settings.database_file == ":memory:"


def test_blank_database_path_falls_back_to_default() -> None:
    settings = load_settings({"APP_ENV": "test", "DATABASE_PATH": "   "})
    assert settings.database_path == DEFAULT_DATABASE_PATH


def test_validate_rejects_empty_database_path() -> None:
    with pytest.raises(ValueError, match="DATABASE_PATH"):
        Settings(app_env="test", log_level="INFO", database_path=" ").validate()


def test_settings_work_without_api_key() -> None:
    settings = load_settings({"APP_ENV": "test"})
    assert settings.openai_api_key is None
