"""Guards for the layering rules in docs/architecture.md and AGENTS.md."""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"


def _imports(path: Path) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _all_imports(package: str) -> set[str]:
    found: set[str] = set()
    for path in (SRC / package).rglob("*.py"):
        found |= _imports(path)
    return found


def _project(modules: set[str]) -> set[str]:
    return {m for m in modules if m.split(".")[0] in {"src", "app"}}


def test_common_only_imports_itself() -> None:
    assert all(m.startswith("src.common") for m in _project(_all_imports("common")))


def test_domain_only_imports_itself() -> None:
    assert all(m.startswith("src.domain") for m in _project(_all_imports("domain")))


def test_src_never_imports_the_app_package() -> None:
    """Configuration and startup live in app/; src stays free of them (no package cycle)."""
    for package in ("common", "domain", "data", "services", "documents", "rag", "loan", "policies"):
        assert not any(m.split(".")[0] == "app" for m in _all_imports(package)), package


def test_data_layer_does_not_import_services() -> None:
    assert not any(m.startswith("src.services") for m in _all_imports("data"))


def test_no_ui_or_ai_provider_imports_in_foundation() -> None:
    forbidden = {"streamlit", "openai", "langchain", "langgraph", "chromadb", "sentence_transformers"}
    for package in ("common", "domain", "data", "services"):
        roots = {m.split(".")[0] for m in _all_imports(package)}
        assert not roots & forbidden, f"{package} imports {roots & forbidden}"
