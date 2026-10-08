"""Tests for policy, inconsistency, summary and AI response contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.domain import (
    AIResponse,
    Applicant,
    DocumentEvidence,
    Inconsistency,
    LoanApplication,
    PolicyDocument,
    PolicyQuery,
    UnderwritingSummary,
)
from src.domain.enums import (
    DocumentAvailability,
    DocumentType,
    QueryContext,
    ResponseStatus,
    InconsistencySeverity,
)
from src.domain.underwriting_summary import DocumentStatusEntry


def test_policy_document_requires_version_and_source() -> None:
    policy = PolicyDocument(
        policy_id="POL-001", title="Underwriting Policy", version="2025.1", source="policy.pdf"
    )
    assert policy.metadata == {}
    with pytest.raises(ValidationError):
        PolicyDocument(policy_id="P", title="T", version="", source="s")


def test_policy_query_defaults_and_validation() -> None:
    query = PolicyQuery(query="What is the maximum DTI?")
    assert query.requested_context is QueryContext.POLICY
    assert query.response_requirements.require_citations is True
    with pytest.raises(ValidationError):
        PolicyQuery(query="   ")
    with pytest.raises(ValidationError):
        PolicyQuery(query="x" * 1001)


def test_application_context_requires_application_id() -> None:
    with pytest.raises(ValidationError, match="application_id"):
        PolicyQuery(query="Employer?", requested_context=QueryContext.APPLICATION)
    ok = PolicyQuery(
        query="Employer?", requested_context=QueryContext.APPLICATION, application_id="LOAN-001"
    )
    assert ok.application_id == "LOAN-001"


def test_severity_is_a_controlled_scale() -> None:
    assert [s.name for s in InconsistencySeverity] == ["INFO", "LOW", "MEDIUM", "HIGH"]


def _inconsistency(a: DocumentEvidence, b: DocumentEvidence, **overrides) -> Inconsistency:
    data = dict(
        inconsistency_id="INC-1",
        application_id="LOAN-001",
        field_name="annual_income",
        source_a=a,
        value_a="120000",
        source_b=b,
        value_b="105000",
        description="Application income differs from salary slip.",
        severity=InconsistencySeverity.HIGH,
    )
    data.update(overrides)
    return Inconsistency(**data)


def test_inconsistency_carries_both_sources_and_defaults_to_review(
    evidence: DocumentEvidence, evidence_b: DocumentEvidence
) -> None:
    inc = _inconsistency(evidence, evidence_b)
    assert inc.requires_human_review is True
    assert inc.source_a.document_id != inc.source_b.document_id


def test_inconsistency_severity_must_be_in_scale(
    evidence: DocumentEvidence, evidence_b: DocumentEvidence
) -> None:
    with pytest.raises(ValidationError):
        _inconsistency(evidence, evidence_b, severity="catastrophic")


def test_serious_inconsistency_cannot_skip_review(
    evidence: DocumentEvidence, evidence_b: DocumentEvidence
) -> None:
    with pytest.raises(ValidationError, match="human review"):
        _inconsistency(evidence, evidence_b, requires_human_review=False)
    low = _inconsistency(evidence, evidence_b, severity=InconsistencySeverity.INFO, requires_human_review=False)
    assert low.requires_human_review is False


def test_summary_is_pending_and_cannot_hold_a_decision(
    applicant: Applicant, application: LoanApplication
) -> None:
    summary = UnderwritingSummary(
        application=application,
        applicant=applicant,
        document_status=[
            DocumentStatusEntry(
                document_type=DocumentType.BANK_STATEMENT,
                availability=DocumentAvailability.MISSING,
            )
        ],
        human_review_items=["Bank statement missing"],
    )
    assert summary.decision == "pending_underwriter"
    assert summary.narrative is None
    assert summary.generated_at.tzinfo is not None
    with pytest.raises(ValidationError):
        UnderwritingSummary(application=application, applicant=applicant, decision="approved")


def test_ai_response_ok_requires_evidence(evidence: DocumentEvidence) -> None:
    response = AIResponse(
        answer="Maximum DTI is 43%.",
        evidence=[evidence],
        sources=["application_form.pdf"],
        warnings=["Policy version 2025.1"],
    )
    assert response.answer and response.evidence and response.warnings
    assert response.status is ResponseStatus.OK
    with pytest.raises(ValidationError, match="evidence"):
        AIResponse(answer="Unsupported claim.")


def test_ai_response_no_evidence_must_flag_review() -> None:
    with pytest.raises(ValidationError, match="human review"):
        AIResponse(answer="Not found.", status=ResponseStatus.NO_EVIDENCE)
    response = AIResponse(
        answer="No relevant information found.",
        status=ResponseStatus.NO_EVIDENCE,
        requires_human_review=True,
    )
    assert response.evidence == []


def test_ai_response_has_no_confidence_score() -> None:
    assert "confidence" not in AIResponse.model_fields


def test_models_round_trip_through_json(evidence: DocumentEvidence) -> None:
    response = AIResponse(answer="A", evidence=[evidence])
    restored = AIResponse.model_validate_json(response.model_dump_json())
    assert restored == response
