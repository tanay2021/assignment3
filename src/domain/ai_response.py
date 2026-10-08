"""Generic grounded AI response contract."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from src.domain.base import DomainModel, utc_now
from src.domain.enums import Provenance, ResponseStatus
from src.domain.evidence import DocumentEvidence


class AIResponse(DomainModel):
    """Keeps answer, evidence and warnings in separate fields.

    No confidence score is included because none has a defined basis yet.
    """

    answer: str = Field(description="The answer text only. Evidence and warnings go in their own fields.")
    evidence: list[DocumentEvidence] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    status: ResponseStatus = ResponseStatus.OK
    provenance: Provenance = Provenance.AI_GENERATED
    generated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _grounding_rules(self) -> "AIResponse":
        if self.status is ResponseStatus.OK and not self.evidence:
            raise ValueError("An OK response must include evidence. Use NO_EVIDENCE otherwise.")
        if self.status in (ResponseStatus.NO_EVIDENCE, ResponseStatus.FAILED):
            if not self.requires_human_review:
                raise ValueError(f"A {self.status.value} response must require human review.")
        return self
