"""Builders for valid synthetic domain objects and wired services used across unit tests."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.domain import (
    Applicant,
    Document,
    DocumentEvidence,
    LoanApplication,
)
from src.domain.enums import DocumentType, EmploymentStatus, LoanType
from src.services import Services, create_services


@pytest.fixture
def evidence() -> DocumentEvidence:
    return DocumentEvidence(
        document_id="DOC-001",
        page_number=1,
        source_reference="application_form.pdf",
        snippet="Annual income: $120,000",
        field_name="annual_income",
        extracted_value="120000",
    )


@pytest.fixture
def evidence_b() -> DocumentEvidence:
    return DocumentEvidence(
        document_id="DOC-002",
        page_number=1,
        source_reference="salary_slip.pdf",
        snippet="Annual equivalent: $105,000",
        field_name="annual_income",
        extracted_value="105000",
    )


@pytest.fixture
def applicant() -> Applicant:
    return Applicant(
        applicant_id="APP-001",
        name="Jordan Sample",
        employment_status=EmploymentStatus.SALARIED,
        employer="Example Corp",
        annual_income=Decimal("120000"),
        existing_liabilities=Decimal("850"),
    )


@pytest.fixture
def application() -> LoanApplication:
    return LoanApplication(
        application_id="LOAN-001",
        applicant_id="APP-001",
        loan_type=LoanType.HOME_PURCHASE,
        requested_amount=Decimal("300000"),
        property_value=Decimal("375000"),
        application_date=date(2026, 1, 15),
    )


@pytest.fixture
def document() -> Document:
    return Document(
        document_id="DOC-001",
        application_id="LOAN-001",
        document_type=DocumentType.APPLICATION,
        filename="application_form.pdf",
        source_reference="data/sample_documents/application_form.pdf",
        page_count=2,
    )


@pytest.fixture
def services() -> Services:
    """Services backed by an in-memory SQLite database; no API key needed."""
    wired = create_services(":memory:")
    yield wired
    wired.database.close()


@pytest.fixture(autouse=True)
def isolate_database_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests must never open the real project database, even by accident."""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
