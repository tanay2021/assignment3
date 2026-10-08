"""The application foundation imports and initializes cleanly without Streamlit or an API key."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

from app.bootstrap import initialize_application
from app.config import Settings

UI_DIR = Path(__file__).resolve().parents[2] / "app" / "ui"


def _settings(tmp_path) -> Settings:
    return Settings(
        app_env="test", log_level="INFO", database_path=str(tmp_path / "poc.sqlite3")
    )


def test_initialize_application_without_api_key(tmp_path) -> None:
    context = initialize_application(_settings(tmp_path))
    try:
        assert context.settings.openai_api_key is None
        assert context.services.policies is not None
        assert (tmp_path / "poc.sqlite3").exists()
    finally:
        context.services.database.close()


def test_initialization_can_repeat(tmp_path) -> None:
    first = initialize_application(_settings(tmp_path))
    second = initialize_application(_settings(tmp_path))
    first.services.database.close()
    second.services.database.close()


def test_ui_entry_point_imports_without_streamlit() -> None:
    sys.modules.pop("app.ui.streamlit_app", None)
    module = importlib.import_module("app.ui.streamlit_app")
    assert callable(module.main)
    assert module.WORKFLOW_STAGES == (
        "Loan Package",
        "Documents",
        "Intelligence",
        "Policy Assistant",
        "Underwriting Summary",
    )
    assert "streamlit" not in {
        alias.name
        for node in ast.walk(ast.parse((UI_DIR / "streamlit_app.py").read_text(encoding="utf-8")))
        if isinstance(node, ast.Import) and node.col_offset == 0
        for alias in node.names
    }


def test_ui_does_not_reach_around_the_service_layer() -> None:
    forbidden_prefixes = ("src.data", "sqlite3", "openai", "langchain", "chromadb")
    for path in UI_DIR.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not [n for n in names if n.startswith(forbidden_prefixes)], path.name
