"""Configuration helpers for the local project foundation.

This module intentionally keeps the configuration surface small and explicit so
future AI and document-processing modules can add settings without breaking the
base setup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from dotenv import load_dotenv

from src.common.constants import IN_MEMORY_DATABASE

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / ".env"

DEFAULT_DATABASE_PATH = "data/loan_poc.sqlite3"

VALID_ENVIRONMENTS ={"development", "staging", "production", "test"}
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _get_environ(environ: Mapping[str, str] | None = None) -> Mapping[str, str]:
    """Return the environment mapping and load .env for local work."""
    if environ is None:
        load_dotenv(ENV_FILE, override=False)
        return os.environ
    return environ


@dataclass(frozen=True)
class Settings:
    """Typed application configuration."""

    app_env: str
    log_level: str
    openai_api_key: str | None = None
    database_path: str = DEFAULT_DATABASE_PATH

    @property
    def database_file(self) -> str:
        """Return the SQLite location, resolving relative paths against the project root."""
        if self.database_path == IN_MEMORY_DATABASE:
            return self.database_path
        path = Path(self.database_path)
        return str(path if path.is_absolute() else ROOT_DIR / path)

    def validate(self) -> None:
        """Raise clear exceptions for invalid runtime config."""
        if not self.app_env:
            raise ValueError("APP_ENV must be set.")

        if not self.database_path.strip():
            raise ValueError("DATABASE_PATH cannot be empty.")

        if self.app_env.lower() not in VALID_ENVIRONMENTS:
            allowed = ", ".join(sorted(VALID_ENVIRONMENTS))
            raise ValueError(f"APP_ENV must be one of: {allowed}")

        normalized_log_level = self.log_level.upper()
        if normalized_log_level not in VALID_LOG_LEVELS:
            allowed = ", ".join(sorted(VALID_LOG_LEVELS))
            raise ValueError(f"LOG_LEVEL must be one of: {allowed}")

        if self.openai_api_key is not None and not self.openai_api_key.strip():
            raise ValueError("OPENAI_API_KEY cannot be empty.")


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Load application settings from environment variables.

    Missing values are treated as a configuration error when the caller provides
    an explicit environment mapping. When the application is running with the
    project .env file, a development default is acceptable so local setup stays
    simple for learners.
    """
    env = _get_environ(environ)

    if environ is None:
        app_env = (env.get("APP_ENV") or "development").strip().lower()
    else:
        app_env = env.get("APP_ENV")
        if app_env is None or not app_env.strip():
            raise ValueError("APP_ENV must be set.")
        app_env = app_env.strip().lower()

    log_level = (env.get("LOG_LEVEL") or "INFO").strip().upper()
    openai_api_key = (env.get("OPENAI_API_KEY") or "").strip() or None

    database_path = (env.get("DATABASE_PATH") or "").strip() or DEFAULT_DATABASE_PATH

    settings = Settings(
        app_env=app_env,
        log_level=log_level,
        openai_api_key=openai_api_key,
        database_path=database_path,
    )
    settings.validate()
    return settings
