"""Project health check for the initial engineering foundation."""

from __future__ import annotations

import importlib
import platform
from typing import Any

from app.config import ROOT_DIR, load_settings
from app.logging_config import setup_logging

REQUIRED_DIRECTORIES = [
    "app",
    "src",
    "src/documents",
    "src/rag",
    "src/loan",
    "src/policies",
    "src/services",
    "tests",
    "tests/unit",
    "tests/integration",
    "data",
    "data/sample_documents",
    "data/sample_policies",
    "logs",
]

REQUIRED_IMPORTS = [
    "dotenv",
    "pytest",
    "langchain",
    "langgraph",
    "openai",
    "fitz",
    "sentence_transformers",
    "chromadb",
]


def check_python_version() -> str:
    """Return the runtime Python version."""
    return platform.python_version()


def check_required_imports() -> tuple[list[str], list[str]]:
    """Check key runtime imports and report failures without exposing secrets."""
    available: list[str] = []
    missing: list[str] = []

    for module_name in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - health check only
            missing.append(f"{module_name}: {exc.__class__.__name__}: {exc}")
        else:
            available.append(module_name)

    return available, missing


def run_health_check() -> dict[str, Any]:
    """Run a lightweight environment validation tailored to the POC foundation."""
    result: dict[str, Any] = {
        "status": "ok",
        "python_version": check_python_version(),
        "issues": [],
        "directories": {},
        "logger_ready": False,
    }

    try:
        settings = load_settings()
        result["app_env"] = settings.app_env
        result["log_level"] = settings.log_level
    except ValueError as exc:
        result["status"] = "error"
        result["issues"].append(f"Configuration error: {exc}")
        result["app_env"] = "unknown"
        result["log_level"] = "unknown"
        settings = None

    for relative_directory in REQUIRED_DIRECTORIES:
        path = ROOT_DIR / relative_directory
        exists = path.exists()
        result["directories"][relative_directory] = exists
        if not exists:
            result["issues"].append(f"Missing required directory: {relative_directory}")

    _, missing_imports = check_required_imports()
    for missing in missing_imports:
        result["issues"].append(f"Import failure: {missing}")

    if settings is not None:
        try:
            logger = setup_logging(settings.log_level)
            result["logger_ready"] = logger is not None
        except Exception as exc:  # pragma: no cover - defensive behavior
            result["status"] = "error"
            result["issues"].append(f"Logging error: {exc}")

    if result["issues"]:
        result["status"] = "error"

    return result


def main() -> int:
    """Run the health check as a command-line script."""
    check_result = run_health_check()

    print(f"Python version: {check_result['python_version']}")
    print(f"Environment: {check_result.get('app_env', 'unknown')}")
    print(f"Log level: {check_result.get('log_level', 'unknown')}")

    if check_result["status"] == "ok":
        print("Health check passed: the project foundation is ready for incremental development.")
        return 0

    print("Health check failed. Review the issues below:")
    for issue in check_result["issues"]:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
