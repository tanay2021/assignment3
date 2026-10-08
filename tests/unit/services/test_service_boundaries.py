"""Service boundaries: valid input in, predictable results out, controlled errors for the rest.

No AI is involved and nothing is mocked beyond a repository that fails on purpose.
"""

from __future__ import annotations

import pytest

from src.common.exceptions import (
    ApplicationError,
    DataAccessError,
    NotFoundError,
    PolicyError,
    ValidationError,
)
from src.data import SqliteApplicantRepository, SqliteDatabase
from src.domain import Applicant, Document, LoanApplication, PolicyQuery, UnderwritingSummary
from src.domain.enums import DocumentAvailability, ProcessingStatus, QueryContext
from src.services import LoanApplicationService, Services


@pytest.fixture
def seeded(
    services: Services, applicant: Applicant, application: LoanApplication, document: Document
) -> Services:
    services.loan_applications.register_applicant(applicant)
    services.loan_applications.submit_application(application)
    services.documents.register_document(document)
    return services


# ------------------------------------------------------------ accept valid models


def test_valid_models_are_accepted_and_returned_unchanged(
    services: Services, applicant: Applicant, application: LoanApplication, document: Document
) -> None:
    assert services.loan_applications.register_applicant(applicant) == applicant
    assert services.loan_applications.submit_application(application) == application
    assert services.documents.register_document(document) == document


def test_valid_policy_query_is_built_with_defaults(services: Services) -> None:
    query = services.policies.create_query("What is the maximum DTI?")
    assert isinstance(query, PolicyQuery)
    assert query.requested_context is QueryContext.POLICY
    assert query.application_id is None


def test_application_scoped_query_is_accepted_with_an_id(services: Services) -> None:
    query = services.policies.create_query(
        "Who is the employer?", application_id="LOAN-001", context=QueryContext.APPLICATION
    )
    assert query.application_id == "LOAN-001"


def test_enum_context_may_be_given_as_text(services: Services) -> None:
    query = services.policies.create_query("Q?", application_id="L", context="policy_and_application")
    assert query.requested_context is QueryContext.POLICY_AND_APPLICATION


# ------------------------------------------------------------ reject invalid input


@pytest.mark.parametrize("bad", [None, {}, "text", 42, object()])
def test_services_reject_values_that_are_not_domain_models(services: Services, bad) -> None:
    with pytest.raises(ValidationError):
        services.loan_applications.register_applicant(bad)
    with pytest.raises(ValidationError):
        services.loan_applications.submit_application(bad)
    with pytest.raises(ValidationError):
        services.documents.register_document(bad)
    with pytest.raises(ValidationError):
        services.policies.answer(bad)


def test_services_reject_the_wrong_model_type(
    services: Services, applicant: Applicant, application: LoanApplication
) -> None:
    with pytest.raises(ValidationError, match="Applicant"):
        services.loan_applications.register_applicant(application)
    with pytest.raises(ValidationError, match="LoanApplication"):
        services.loan_applications.submit_application(applicant)


@pytest.mark.parametrize("bad_id", ["", "   ", None, 7])
def test_blank_or_non_text_ids_are_validation_errors_not_lookups(services: Services, bad_id) -> None:
    calls = [
        services.loan_applications.get_applicant,
        services.loan_applications.get_application,
        services.loan_applications.list_applications,
        services.documents.get_document,
        services.documents.list_documents,
        services.underwriting.prepare_summary,
    ]
    for call in calls:
        with pytest.raises(ValidationError):
            call(bad_id)


@pytest.mark.parametrize("question", ["", "   ", "x" * 1001, None, 123])
def test_invalid_questions_are_rejected_with_a_readable_message(
    services: Services, question
) -> None:
    with pytest.raises(ValidationError) as info:
        services.policies.create_query(question)
    assert info.value.user_message.startswith("The question is not valid")


def test_application_context_without_id_is_rejected(services: Services) -> None:
    with pytest.raises(ValidationError, match="application_id"):
        services.policies.create_query("Q?", context=QueryContext.APPLICATION)


def test_unknown_context_and_status_values_are_rejected(seeded: Services) -> None:
    with pytest.raises(ValidationError, match="context"):
        seeded.policies.create_query("Q?", context="everything")
    with pytest.raises(ValidationError, match="status"):
        seeded.documents.update_processing_status("DOC-001", "half_done")
    with pytest.raises(ValidationError):
        seeded.documents.update_processing_status("DOC-001", None)
    assert seeded.documents.get_document("DOC-001").processing_status is ProcessingStatus.PENDING


# ------------------------------------------------------------ predictable results


def test_reads_return_what_was_stored(seeded: Services, applicant, application, document) -> None:
    assert seeded.loan_applications.get_applicant("APP-001") == applicant
    assert seeded.loan_applications.get_application("LOAN-001") == application
    assert seeded.documents.get_document("DOC-001") == document


def test_ids_are_trimmed_before_lookup(seeded: Services, application: LoanApplication) -> None:
    assert seeded.loan_applications.get_application("  LOAN-001 ") == application


def test_registering_twice_is_idempotent(
    seeded: Services, applicant: Applicant, document: Document
) -> None:
    seeded.loan_applications.register_applicant(applicant)
    seeded.documents.register_document(document)
    assert len(seeded.documents.list_documents("LOAN-001")) == 1
    assert len(seeded.loan_applications.list_applications("APP-001")) == 1


def test_listings_are_empty_lists_not_errors_when_nothing_exists(services: Services) -> None:
    assert services.loan_applications.list_applications("NOBODY") == []
    assert services.documents.list_documents("NOTHING") == []


def test_listing_order_is_stable(seeded: Services, document: Document) -> None:
    for doc_id in ("DOC-9", "DOC-3", "DOC-5"):
        seeded.documents.register_document(document.model_copy(update={"document_id": doc_id}))
    ids = [d.document_id for d in seeded.documents.list_documents("LOAN-001")]
    assert ids == sorted(ids) == ["DOC-001", "DOC-3", "DOC-5", "DOC-9"]


def test_status_update_changes_only_status_fields(seeded: Services, document: Document) -> None:
    updated = seeded.documents.update_processing_status(
        "DOC-001", ProcessingStatus.UNREADABLE, "No text layer"
    )
    expected = document.model_copy(
        update={"processing_status": ProcessingStatus.UNREADABLE, "status_detail": "No text layer"}
    )
    assert updated == expected
    assert seeded.documents.get_document("DOC-001") == expected


def test_status_may_be_given_as_text(seeded: Services) -> None:
    updated = seeded.documents.update_processing_status("DOC-001", "ingested")
    assert updated.processing_status is ProcessingStatus.INGESTED


def test_summary_is_repeatable_and_makes_no_decision(seeded: Services) -> None:
    first = seeded.underwriting.prepare_summary("LOAN-001")
    second = seeded.underwriting.prepare_summary("LOAN-001")
    assert isinstance(first, UnderwritingSummary)
    assert first.model_dump(exclude={"generated_at"}) == second.model_dump(exclude={"generated_at"})
    assert first.decision == "pending_underwriter"
    assert [e.availability for e in first.document_status] == [DocumentAvailability.PRESENT]
    assert first.human_review_items == []


def test_summary_with_no_documents_is_valid_and_empty(
    services: Services, applicant: Applicant, application: LoanApplication
) -> None:
    services.loan_applications.register_applicant(applicant)
    services.loan_applications.submit_application(application)
    summary = services.underwriting.prepare_summary("LOAN-001")
    assert summary.document_status == []


# ------------------------------------------------------------ controlled exceptions


def test_missing_records_raise_not_found_with_the_id(seeded: Services, document: Document) -> None:
    with pytest.raises(NotFoundError, match="NOPE"):
        seeded.loan_applications.get_application("NOPE")
    with pytest.raises(NotFoundError, match="NOPE"):
        seeded.documents.update_processing_status("NOPE", ProcessingStatus.INGESTED)
    with pytest.raises(NotFoundError, match="NOPE"):
        seeded.underwriting.prepare_summary("NOPE")
    with pytest.raises(NotFoundError, match="LOAN-X"):
        seeded.documents.register_document(
            document.model_copy(update={"application_id": "LOAN-X"})
        )


def test_application_for_unknown_applicant_is_refused(
    services: Services, application: LoanApplication
) -> None:
    with pytest.raises(NotFoundError, match="APP-001"):
        services.loan_applications.submit_application(application)
    assert services.loan_applications.list_applications("APP-001") == []


def test_policy_answering_raises_a_policy_error_for_now(services: Services) -> None:
    query = services.policies.create_query("What is the maximum DTI?")
    with pytest.raises(PolicyError) as info:
        services.policies.answer(query)
    assert "not available yet" in info.value.user_message


def test_every_failure_is_an_application_error(seeded: Services) -> None:
    """Bad calls never leak AttributeError, TypeError, KeyError or library errors."""
    bad_calls = [
        lambda: seeded.loan_applications.register_applicant(None),
        lambda: seeded.loan_applications.get_application(""),
        lambda: seeded.loan_applications.get_application("NOPE"),
        lambda: seeded.documents.get_document(None),
        lambda: seeded.documents.update_processing_status("DOC-001", "bogus"),
        lambda: seeded.documents.update_processing_status("NOPE", ProcessingStatus.EMPTY),
        lambda: seeded.policies.create_query(""),
        lambda: seeded.policies.create_query("Q?", context="bogus"),
        lambda: seeded.policies.answer("not a query"),
        lambda: seeded.underwriting.prepare_summary(" "),
    ]
    for call in bad_calls:
        with pytest.raises(ApplicationError):
            call()


def test_storage_failures_surface_as_data_access_errors(
    applicant: Applicant, application: LoanApplication
) -> None:
    database = SqliteDatabase(":memory:")
    applicants = SqliteApplicantRepository(database)
    database.close()

    class UnusedApplications:
        def save(self, *_args) -> None: ...
        def get(self, *_args) -> None: ...

    service = LoanApplicationService(applicants, UnusedApplications())  # type: ignore[arg-type]
    with pytest.raises(DataAccessError) as info:
        service.register_applicant(applicant)
    message = info.value.user_message.lower()
    assert "sqlite" not in message and "closed" not in message
    with pytest.raises(DataAccessError):
        service.get_applicant("APP-001")
