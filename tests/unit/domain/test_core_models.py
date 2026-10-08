"""Tests for applicant, application, document, evidence and extracted information."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.domain import (
    Applicant,
    Document,
    DocumentEvidence,
    ExtractedInformation,
    LoanApplication,
)
from src.domain.enums import (
    LoanStatus,
    Confidence,
    DocumentType,
    LoanType,
    ProcessingStatus,
    Provenance,
)


def test_applicant_valid(applicant: Applicant) -> None:
    assert applicant.annual_income == Decimal("120000")
    assert applicant.other_income is None


def test_applicant_rejects_negative_income_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Applicant(applicant_id="A", name="N", annual_income=Decimal("-1"))
    with pytest.raises(ValidationError):
        Applicant(applicant_id="A", name="N", ssn="000-00-0000")


def test_application_defaults_and_has_no_decision_field(application: LoanApplication) -> None:
    assert application.status is LoanStatus.SUBMITTED
    assert not {"decision", "approved", "approval", "rejected"} & set(LoanApplication.model_fields)


def test_application_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        LoanApplication(
            application_id="L",
            applicant_id="A",
            loan_type=LoanType.PERSONAL,
            requested_amount=Decimal("0"),
            application_date="2026-01-01",
        )


def test_document_defaults_to_pending_and_accepts_metadata() -> None:
    doc = Document(
        document_id="DOC-1",
        application_id="LOAN-001",
        document_type=DocumentType.INCOME,
        filename="salary_slip.pdf",
        source_reference="data/sample_documents/salary_slip.pdf",
        metadata={"pages_with_text": 1, "scanned": False},
    )
    assert doc.processing_status is ProcessingStatus.PENDING
    assert doc.page_count is None
    assert doc.metadata["scanned"] is False


def test_document_rejects_negative_page_count() -> None:
    with pytest.raises(ValidationError):
        Document(
            document_id="D",
            application_id="L",
            document_type=DocumentType.UNKNOWN,
            filename="f.pdf",
            source_reference="f.pdf",
            page_count=-1,
        )


def test_evidence_requires_content_and_page(evidence: DocumentEvidence) -> None:
    with pytest.raises(ValidationError):
        DocumentEvidence(document_id="D", page_number=1, source_reference="f.pdf")
    with pytest.raises(ValidationError):
        DocumentEvidence(document_id="D", page_number=0, source_reference="f.pdf", snippet="x")
    assert evidence.page_number == 1


def test_evidence_is_immutable(evidence: DocumentEvidence) -> None:
    with pytest.raises(ValidationError):
        evidence.page_number = 2  # type: ignore[misc]


def test_extracted_information_supports_new_fields_without_schema_change(
    evidence: DocumentEvidence,
) -> None:
    info = ExtractedInformation(
        application_id="LOAN-001",
        field_name="any_future_field",
        value="abc",
        evidence=[evidence],
        verified_in_source=True,
    )
    assert info.is_traceable
    assert info.provenance is Provenance.EXTRACTED
    assert info.confidence is None


def test_extracted_information_keeps_typed_values() -> None:
    info = ExtractedInformation(
        application_id="L",
        field_name="annual_income",
        value="$120,000",
        normalized_value=Decimal("120000"),
    )
    assert info.normalized_value == Decimal("120000")
    assert not info.is_traceable


def test_verified_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="evidence"):
        ExtractedInformation(
            application_id="L", field_name="f", value="v", verified_in_source=True
        )


def test_confidence_is_qualitative_only() -> None:
    with pytest.raises(ValidationError):
        ExtractedInformation(application_id="L", field_name="f", value="v", confidence=0.93)
    info = ExtractedInformation(
        application_id="L", field_name="f", value="v", confidence=Confidence.LOW
    )
    assert info.confidence is Confidence.LOW
