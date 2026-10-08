"""Extracted information: one field value with its traceability."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import Field, model_validator

from src.domain.base import DomainModel
from src.domain.enums import Confidence, Provenance
from src.domain.evidence import DocumentEvidence

# Typed normalization only. Raw text stays in ``value`` so a JSON round trip never changes it.
NormalizedValue = Decimal | date | bool


class ExtractedInformation(DomainModel):
    """A single field. New fields are new field_name values, not new attributes."""

    application_id: str = Field(min_length=1)
    field_name: str = Field(min_length=1, description="Canonical name, e.g. annual_income.")
    value: str = Field(description="Value as written in the source, or as produced (always text).")
    normalized_value: Optional[NormalizedValue] = Field(
        default=None, description="Typed form (number, date or flag) when useful."
    )
    provenance: Provenance = Provenance.EXTRACTED
    confidence: Optional[Confidence] = Field(
        default=None, description="None unless a defined rule sets it. No invented scores."
    )
    evidence: list[DocumentEvidence] = Field(default_factory=list)
    verified_in_source: bool = False
    confirmed_by_human: bool = False

    @model_validator(mode="after")
    def _verified_needs_evidence(self) -> "ExtractedInformation":
        if self.verified_in_source and not self.evidence:
            raise ValueError("verified_in_source requires at least one evidence item.")
        return self

    @property
    def is_traceable(self) -> bool:
        return bool(self.evidence)
