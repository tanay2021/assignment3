"""Input guards shared by services so bad input becomes a controlled ValidationError."""

from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar

from src.common.exceptions import ValidationError

T = TypeVar("T")
E = TypeVar("E", bound=Enum)


def require_model(value: Any, model_type: type[T], label: str) -> T:
    """Accept only an already-validated domain model of the expected type."""
    if not isinstance(value, model_type):
        raise ValidationError(f"{label} must be a {model_type.__name__}.")
    return value


def require_id(value: Any, label: str) -> str:
    """Accept only a non-blank string identifier."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} cannot be empty.")
    return value.strip()


def require_enum(value: Any, enum_type: type[E], label: str) -> E:
    """Accept an enum member or its string value."""
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed = ", ".join(member.value for member in enum_type)
        raise ValidationError(f"{label} must be one of: {allowed}.") from exc
