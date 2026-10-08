"""Guards for the data model design principles in AGENTS.md.

Keeps domain models small, explicitly typed, free of I/O and independent of
Streamlit, OpenAI and ChromaDB, so they stay easy to understand and reuse.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import src.domain as domain
from src.domain.base import DomainModel

DOMAIN_DIR = Path(domain.__file__).parent
MAX_FIELDS = 12
ALLOWED_THIRD_PARTY = {"pydantic"}
ALLOWED_STDLIB = {"__future__", "datetime", "decimal", "enum", "typing"}

MODELS = [getattr(domain, name) for name in domain.__all__]


def _domain_files() -> list[Path]:
    return sorted(DOMAIN_DIR.glob("*.py"))


def _imported_roots(path: Path) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


@pytest.mark.parametrize("path", _domain_files(), ids=lambda p: p.name)
def test_domain_modules_import_only_pydantic_stdlib_basics_and_themselves(path: Path) -> None:
    """No UI, AI, vector store, database, network, filesystem or logging in models."""
    allowed = ALLOWED_THIRD_PARTY | ALLOWED_STDLIB | {"src"}
    assert _imported_roots(path) <= allowed, path.name


@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__name__)
def test_models_are_small_and_cohesive(model: type[DomainModel]) -> None:
    assert len(model.model_fields) <= MAX_FIELDS


@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__name__)
def test_models_contain_validators_only_no_workflow_methods(model: type[DomainModel]) -> None:
    own = [
        name
        for name, member in vars(model).items()
        if inspect.isfunction(member) and not name.startswith("__")
    ]
    assert all(name.startswith("_") for name in own), own


def test_no_untyped_fields() -> None:
    for model in MODELS:
        for name, field in model.model_fields.items():
            assert field.annotation is not None, f"{model.__name__}.{name}"
    for path in _domain_files():
        assert "typing import Any" not in path.read_text(encoding="utf-8"), path.name


def test_all_models_share_the_strict_base() -> None:
    for model in MODELS:
        assert issubclass(model, DomainModel)
        assert model.model_config.get("extra") == "forbid"


def test_public_api_lists_every_model_defined_in_the_package() -> None:
    defined = {
        name
        for path in _domain_files()
        for node in ast.parse(path.read_text(encoding="utf-8")).body
        if isinstance(node, ast.ClassDef)
        for name in [node.name]
        if any(
            isinstance(base, ast.Name) and base.id == "DomainModel" for base in node.bases
        )
    }
    assert defined == set(domain.__all__)


@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__name__)
def test_every_model_has_a_one_line_docstring(model: type[DomainModel]) -> None:
    doc = model.__doc__
    assert doc and doc.strip(), model.__name__
    assert doc is not DomainModel.__doc__, f"{model.__name__} inherits the base docstring"
