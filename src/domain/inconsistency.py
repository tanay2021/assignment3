"""Cross-document inconsistency contract."""

from __future__ import annotations

from typing import Optional

from pydantic import Field, model_validator

from src.domain.base import DomainModel
from src.domain.enums import InconsistencySeverity, ReviewStatus
from src.domain.evidence import DocumentEvidence


class Inconsistency(DomainModel):
    """Two sources that disagree about the same field, with evidence for each."""

    inconsistency_id: str = Field(min_length=1)
    application_id: str = Field(min_length=1)
    field_name: str = Field(min_length=1)
    source_a: DocumentEvidence
    value_a: str
    source_b: DocumentEvidence
    value_b: str
    description: str = Field(min_length=1)
    severity: InconsistencySeverity
    requires_human_review: bool = True
    review_status: ReviewStatus = ReviewStatus.OPEN
    reviewer_note: Optional[str] = Field(default=None, description="Entered by the human reviewer.")

    @model_validator(mode="after")
    def _serious_needs_review(self) -> "Inconsistency":
        serious = (InconsistencySeverity.MEDIUM, InconsistencySeverity.HIGH)
        if self.severity in serious and not self.requires_human_review:
            raise ValueError("MEDIUM and HIGH inconsistencies must require human review.")
        return self
