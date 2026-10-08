"""Service foundation tests. Everything runs offline without an API key."""

from __future__ import annotations

import logging

import pytest

from src.common.exceptions import (
    DataAccessError,
    NotFoundError,
    PolicyError,
    ValidationError,
)
from src.domain import Applicant, Document, LoanApplication
from src.domain.enums import DocumentAvailability, ProcessingStatus, QueryContext
from src.services import LoanApplicationService, Services


def _seed(services: Services, applicant: Applicant, application: LoanApplication) -> None:
    services.loan_applications.register_applicant(applicant)
    services.loan_applications.submit_application(application)


def test_application_requires_a_registered_applicant(
    services: Services, application: LoanApplication
) -> None:
    with pytest.raises(NotFoundError, match="APP-001"):
        services.loan_applications.submit_application(application)


def test_register_and_retrieve(
    services: Services, applicant: Applicant, application: LoanApplication
) -> None:
    _seed(services, applicant, application)
    assert services.loan_applications.get_applicant("APP-001") == applicant
    assert services.loan_applications.get_application("LOAN-001") == application
    assert services.loan_applications.list_applications("APP-001") == [application]


def test_unknown_records_raise_not_found(services: Services) -> None:
    with pytest.raises(NotFoundError):
        services.loan_applications.get_application("X")
    with pytest.raises(NotFoundError):
        services.documents.get_document("X")


def test_document_requires_existing_application(services: Services, document: Document) -> None:
    with pytest.raises(NotFoundError):
        services.documents.register_document(document)


def test_document_status_update(
    services: Services, applicant: Applicant, application: LoanApplication, document: Document
) -> None:
    _seed(services, applicant, application)
    services.documents.register_document(document)
    updated = services.documents.update_processing_status(
        "DOC-001", ProcessingStatus.UNREADABLE, "No extractable text"
    )
    assert updated.processing_status is ProcessingStatus.UNREADABLE
    assert services.documents.get_document("DOC-001").status_detail == "No extractable text"


def test_policy_query_validation_is_translated(services: Services) -> None:
    query = services.policies.create_query("What is the maximum DTI?")
    assert query.requested_context is QueryContext.POLICY
    with pytest.raises(ValidationError):
        services.policies.create_query("   ")
    with pytest.raises(ValidationError, match="application_id"):
        services.policies.create_query("Employer?", context=QueryContext.APPLICATION)


def test_policy_answering_is_not_available_yet(services: Services) -> None:
    query = services.policies.create_query("What is the maximum DTI?")
    with pytest.raises(PolicyError):
        services.policies.answer(query)


def test_summary_skeleton_has_no_decision_and_flags_unreadable_documents(
    services: Services, applicant: Applicant, application: LoanApplication, document: Document
) -> None:
    _seed(services, applicant, application)
    services.documents.register_document(document)
    services.documents.register_document(
        document.model_copy(
            update={"document_id": "DOC-002", "processing_status": ProcessingStatus.EMPTY}
        )
    )
    summary = services.underwriting.prepare_summary("LOAN-001")
    availability = {e.document_id: e.availability for e in summary.document_status}
    assert availability == {
        "DOC-001": DocumentAvailability.PRESENT,
        "DOC-002": DocumentAvailability.UNREADABLE,
    }
    assert summary.human_review_items == ["Document DOC-002 could not be read."]
    assert summary.decision == "pending_underwriter"
    assert summary.narrative is None
    assert summary.financial_information == []


def test_summary_for_unknown_application_raises(services: Services) -> None:
    with pytest.raises(NotFoundError):
        services.underwriting.prepare_summary("missing")


def test_data_errors_propagate_without_raw_details(
    applicant: Applicant, application: LoanApplication
) -> None:
    class BrokenRepository:
        def save(self, *_args) -> None:
            raise DataAccessError("Database operation failed.")

        def get(self, *_args):
            raise DataAccessError("Database operation failed.")

    service = LoanApplicationService(BrokenRepository(), BrokenRepository())  # type: ignore[arg-type]
    with pytest.raises(DataAccessError) as info:
        service.register_applicant(applicant)
    assert "try again" in info.value.user_message


def test_logging_omits_personal_details(
    services: Services,
    applicant: Applicant,
    application: LoanApplication,
    caplog: pytest.LogCaptureFixture,
) -> None:
    project_logger = logging.getLogger("loan_processing_ai_poc")
    old_level = project_logger.level
    # The project logger does not propagate to root, so attach the capture handler to it.
    project_logger.addHandler(caplog.handler)
    project_logger.setLevel(logging.DEBUG)
    try:
        _seed(services, applicant, application)
    finally:
        project_logger.removeHandler(caplog.handler)
        project_logger.setLevel(old_level)
    text = caplog.text
    assert "APP-001" in text and "LOAN-001" in text
    assert applicant.name not in text
    assert applicant.employer not in text
    assert "120000" not in text
