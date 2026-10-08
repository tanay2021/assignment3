"""Policy document contract."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import Field

from src.domain.base import DomainModel
from src.domain.document import MetadataValue


class PolicyDocument(DomainModel):
    """Metadata about a policy document."""

    policy_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    version: str = Field(min_length=1)
    effective_date: Optional[date] = None
    source: str = Field(min_length=1, description="File path or other locator.")
    metadata: dict[str, MetadataValue] = Field(default_factory=dict)
