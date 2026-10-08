"""Data-integrity validation. These tests check shape and sanity, never approval rules."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.domain import Applicant, Document, DocumentEvidence, LoanApplication
from src.domain.enums import DocumentType, LoanType


@pytest.mark.parametrize("bad_id", ["", "   "])
def test_ids_cannot_be_empty_or_blank(bad_id: str) -> None:
    with pytest.raises(ValidationError):
        Applicant(applicant_id=bad_id, name="N")
    with pytest.raises(ValidationError):
        LoanApplication(
            application_id=bad_id,
            applicant_id="A",
            loan_type=LoanType.PERSONAL,
            requested_amount=Decimal("1"),
            application_date=date(2026, 1, 1),
        )
    with pytest.raises(ValidationError):
        LoanApplication(
            application_id="L",
            applicant_id=bad_id,
            loan_type=LoanType.PERSONAL,
            requested_amount=Decimal("1"),
            application_date=date(2026, 1, 1),
        )


def test_loan_amount_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        LoanApplication(
            application_id="L",
            applicant_id="A",
            loan_type=LoanType.PERSONAL,
            requested_amount=Decimal("-5"),
            application_date=date(2026, 1, 1),
        )


@pytest.mark.parametrize("field", ["annual_income", "other_income", "existing_liabilities"])
def test_applicant_money_fields_cannot_be_negative(field: str) -> None:
    with pytest.raises(ValidationError):
        Applicant(applicant_id="A", name="N", **{field: Decimal("-1")})


@pytest.mark.parametrize("page", [-1, 0])
def test_page_number_must_be_positive(page: int) -> None:
    with pytest.raises(ValidationError):
        DocumentEvidence(document_id="D", page_number=page, source_reference="f.pdf", snippet="x")


@pytest.mark.parametrize("field", ["document_id", "application_id", "filename", "source_reference"])
def test_required_document_fields_cannot_be_empty(field: str) -> None:
    data = dict(
        document_id="D",
        application_id="L",
        document_type=DocumentType.INCOME,
        filename="f.pdf",
        source_reference="f.pdf",
    )
    data[field] = " "
    with pytest.raises(ValidationError):
        Document(**data)


def test_enum_values_must_be_valid() -> None:
    with pytest.raises(ValidationError):
        Document(
            document_id="D",
            application_id="L",
            document_type="passport_photo",
            filename="f.pdf",
            source_reference="f.pdf",
        )
    with pytest.raises(ValidationError):
        LoanApplication(
            application_id="L",
            applicant_id="A",
            loan_type="yacht",
            requested_amount=Decimal("1"),
            application_date=date(2026, 1, 1),
        )


def test_models_hold_no_underwriting_policy_rules() -> None:
    """Domain models validate data integrity only, so no ratio or eligibility fields exist."""
    forbidden = {"dti", "ltv", "eligible", "approved", "credit_score", "max_dti", "max_ltv"}
    for model in (Applicant, LoanApplication):
        assert not forbidden & {name.lower() for name in model.model_fields}
