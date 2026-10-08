"""Shared base class for domain models."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict


def utc_now() -> datetime:
    """Return the current timezone-aware UTC time (used for generated_at fields)."""
    return datetime.now(timezone.utc)


class DomainModel(BaseModel):
    """Base for all domain models.

    Unknown fields are rejected so typos and silent schema drift fail loudly,
    and strings are stripped of surrounding whitespace.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
