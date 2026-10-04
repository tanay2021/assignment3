"""Initial unit tests for the project foundation."""

from __future__ import annotations

import importlib

import pytest

from app.config import load_settings
from app.healthcheck import run_health_check
from app.logging_config import setup_logging


def test_config_loads_expected_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    settings = load_settings()

    assert settings.app_env == "production"
    assert settings.log_level == "DEBUG"
    assert settings.openai_api_key == "test-key"


def test_missing_or_invalid_configuration_raises() -> None:
    with pytest.raises(ValueError, match="APP_ENV"):
        load_settings({"APP_ENV": "", "LOG_LEVEL": "INFO"})

    with pytest.raises(ValueError, match="LOG_LEVEL"):
        load_settings({"APP_ENV": "development", "LOG_LEVEL": "VERBOSE"})


def test_logging_initialization_creates_log_file(tmp_path) -> None:
    log_dir = tmp_path / "logs"
    logger = setup_logging(log_level="INFO", log_dir=log_dir)
    logger.info("unit test log message")

    log_file = log_dir / "application.log"
    assert log_file.exists()
    assert "unit test log message" in log_file.read_text(encoding="utf-8")


def test_project_import_health() -> None:
    app_module = importlib.import_module("app")
    config_module = importlib.import_module("app.config")
    logging_module = importlib.import_module("app.logging_config")
    health_module = importlib.import_module("app.healthcheck")

    assert app_module is not None
    assert hasattr(config_module, "load_settings")
    assert hasattr(logging_module, "setup_logging")
    assert hasattr(health_module, "run_health_check")


def test_environment_readiness(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    response = run_health_check()

    assert response["status"] == "ok"
    assert response["logger_ready"] is True
    assert response["python_version"]
