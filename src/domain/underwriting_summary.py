"""Underwriting summary contract. Holds data only; no LLM logic."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from src.domain.applicant import Applicant
from src.domain.base import DomainModel, utc_now
from src.domain.enums import DocumentAvailability, DocumentType, InconsistencySeverity
from src.domain.evidence import DocumentEvidence
from src.domain.extracted_information import ExtractedInformation
from src.domain.inconsistency import Inconsistency
from src.domain.loan_application import LoanApplication


class DocumentStatusEntry(DomainModel):
    """Completeness result for one expected document type."""

    document_type: DocumentType
    availability: DocumentAvailability
    document_id: Optional[str] = None
    detail: Optional[str] = None


class PolicyObservation(DomainModel):
    """A policy-related note for the underwriter, with its supporting evidence."""

    text: str = Field(min_length=1)
    evidence: list[DocumentEvidence] = Field(default_factory=list)
    requires_human_review: bool = False


class RiskIndicator(DomainModel):
    """A risk indicator and the rule or evidence behind it."""

    indicator: str = Field(min_length=1)
    basis: str = Field(min_length=1, description="The rule or evidence that triggered the indicator.")
    severity: InconsistencySeverity
    evidence: list[DocumentEvidence] = Field(default_factory=list)


class UnderwritingSummary(DomainModel):
    """Everything the underwriter needs to review a case; the decision stays pending."""

    application: LoanApplication
    applicant: Applicant
    document_status: list[DocumentStatusEntry] = Field(default_factory=list)
    financial_information: list[ExtractedInformation] = Field(default_factory=list)
    inconsistencies: list[Inconsistency] = Field(default_factory=list)
    policy_observations: list[PolicyObservation] = Field(default_factory=list)
    risk_indicators: list[RiskIndicator] = Field(default_factory=list)
    evidence: list[DocumentEvidence] = Field(default_factory=list)
    human_review_items: list[str] = Field(default_factory=list)
    narrative: Optional[str] = Field(default=None, description="AI-generated text, filled in later.")
    generated_at: datetime = Field(default_factory=utc_now)
    decision: Literal["pending_underwriter"] = "pending_underwriter"
