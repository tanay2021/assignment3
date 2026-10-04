"""Integration-style checks for the environment foundation."""

from __future__ import annotations

from app.config import load_settings
from app.healthcheck import run_health_check


def test_environment_is_ready_for_future_development(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_settings()
    health = run_health_check()

    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert health["status"] == "ok"
    assert health["issues"] == []
