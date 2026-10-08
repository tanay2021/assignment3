"""Behaviour every repository implementation must provide.

The same tests run against an in-memory fake, an in-memory SQLite database and a
temporary SQLite file. Nothing here touches the real project database.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pytest

from src.data import (
    ApplicantRepository,
    DocumentRepository,
    LoanApplicationRepository,
    SqliteApplicantRepository,
    SqliteDatabase,
    SqliteDocumentRepository,
    SqliteLoanApplicationRepository,
)
from src.domain import Applicant, Document, LoanApplication
from src.domain.enums import LoanStatus, ProcessingStatus
from src.services import DocumentService, LoanApplicationService
from tests.unit.data.fakes import (
    InMemoryApplicantRepository,
    InMemoryDocumentRepository,
    InMemoryLoanApplicationRepository,
)


@dataclass
class Repos:
    applicants: ApplicantRepository
    applications: LoanApplicationRepository
    documents: DocumentRepository


@pytest.fixture(params=["fake", "sqlite_memory", "sqlite_file"])
def repos(request, tmp_path):
    if request.param == "fake":
        yield Repos(
            InMemoryApplicantRepository(),
            InMemoryLoanApplicationRepository(),
            InMemoryDocumentRepository(),
        )
        return
    path = ":memory:" if request.param == "sqlite_memory" else str(tmp_path / "test.sqlite3")
    database = SqliteDatabase(path)
    yield Repos(
        SqliteApplicantRepository(database),
        SqliteLoanApplicationRepository(database),
        SqliteDocumentRepository(database),
    )
    database.close()


# ---------------------------------------------------------------- create / retrieve


def test_create_and_retrieve_applicant(repos: Repos, applicant: Applicant) -> None:
    repos.applicants.save(applicant)
    assert repos.applicants.get("APP-001") == applicant


def test_create_and_retrieve_application(repos: Repos, application: LoanApplication) -> None:
    repos.applications.save(application)
    assert repos.applications.get("LOAN-001") == application


def test_create_and_retrieve_document(repos: Repos, document: Document) -> None:
    repos.documents.save(document)
    assert repos.documents.get("DOC-001") == document


def test_retrieved_records_are_copies(repos: Repos, applicant: Applicant) -> None:
    repos.applicants.save(applicant)
    first = repos.applicants.get("APP-001")
    first.name = "Changed Locally"
    assert repos.applicants.get("APP-001").name == "Jordan Sample"


# ---------------------------------------------------------------- update


def test_update_applicant(repos: Repos, applicant: Applicant) -> None:
    repos.applicants.save(applicant)
    repos.applicants.save(applicant.model_copy(update={"annual_income": Decimal("130000")}))
    assert repos.applicants.get("APP-001").annual_income == Decimal("130000")


def test_update_application_status(repos: Repos, application: LoanApplication) -> None:
    repos.applications.save(application)
    repos.applications.save(application.model_copy(update={"status": LoanStatus.IN_REVIEW}))
    assert repos.applications.get("LOAN-001").status is LoanStatus.IN_REVIEW
    assert len(repos.applications.list_by_applicant("APP-001")) == 1


def test_update_document_status(repos: Repos, document: Document) -> None:
    repos.documents.save(document)
    repos.documents.save(
        document.model_copy(
            update={"processing_status": ProcessingStatus.INGESTED, "page_count": 3}
        )
    )
    stored = repos.documents.get("DOC-001")
    assert stored.processing_status is ProcessingStatus.INGESTED and stored.page_count == 3
    assert len(repos.documents.list_by_application("LOAN-001")) == 1


# ---------------------------------------------------------------- missing records


def test_missing_record_behaviour(repos: Repos) -> None:
    assert repos.applicants.get("MISSING") is None
    assert repos.applications.get("MISSING") is None
    assert repos.documents.get("MISSING") is None
    assert repos.applications.list_by_applicant("MISSING") == []
    assert repos.documents.list_by_application("MISSING") == []


def test_lookup_does_not_match_partial_or_other_ids(repos: Repos, applicant: Applicant) -> None:
    repos.applicants.save(applicant)
    assert repos.applicants.get("APP-00") is None
    assert repos.applicants.get("app-001") is None


# ---------------------------------------------------------------- listing and isolation


def test_listing_is_scoped_and_ordered(
    repos: Repos, application: LoanApplication, document: Document
) -> None:
    repos.applications.save(application.model_copy(update={"application_id": "LOAN-B"}))
    repos.applications.save(application.model_copy(update={"application_id": "LOAN-A"}))
    repos.applications.save(
        application.model_copy(update={"application_id": "LOAN-C", "applicant_id": "APP-002"})
    )
    assert [a.application_id for a in repos.applications.list_by_applicant("APP-001")] == [
        "LOAN-A",
        "LOAN-B",
    ]

    repos.documents.save(document.model_copy(update={"document_id": "DOC-2"}))
    repos.documents.save(document.model_copy(update={"document_id": "DOC-1"}))
    repos.documents.save(
        document.model_copy(update={"document_id": "DOC-9", "application_id": "LOAN-OTHER"})
    )
    assert [d.document_id for d in repos.documents.list_by_application("LOAN-001")] == [
        "DOC-1",
        "DOC-2",
    ]


def test_record_types_do_not_collide(
    repos: Repos, applicant: Applicant, application: LoanApplication, document: Document
) -> None:
    """The same id string may exist in different repositories without interference."""
    repos.applicants.save(applicant.model_copy(update={"applicant_id": "X-1"}))
    repos.applications.save(application.model_copy(update={"application_id": "X-1"}))
    repos.documents.save(document.model_copy(update={"document_id": "X-1"}))
    assert repos.applicants.get("X-1").applicant_id == "X-1"
    assert repos.applications.get("X-1").application_id == "X-1"
    assert repos.documents.get("X-1").document_id == "X-1"


# ---------------------------------------------------------------- interface is enough for services


def test_services_run_on_any_implementation(
    repos: Repos, applicant: Applicant, application: LoanApplication, document: Document
) -> None:
    loans = LoanApplicationService(repos.applicants, repos.applications)
    docs = DocumentService(repos.documents, repos.applications)
    loans.register_applicant(applicant)
    loans.submit_application(application)
    docs.register_document(document)
    updated = docs.update_processing_status("DOC-001", ProcessingStatus.INGESTED)
    assert updated.processing_status is ProcessingStatus.INGESTED
    assert [d.document_id for d in docs.list_documents("LOAN-001")] == ["DOC-001"]


def test_repository_interfaces_cannot_be_instantiated() -> None:
    for interface in (ApplicantRepository, LoanApplicationRepository, DocumentRepository):
        with pytest.raises(TypeError):
            interface()  # type: ignore[abstract]


# ---------------------------------------------------------------- no production data


def test_file_database_lives_only_in_the_temp_directory(tmp_path) -> None:
    path = tmp_path / "isolated.sqlite3"
    database = SqliteDatabase(str(path))
    SqliteApplicantRepository(database).save(Applicant(applicant_id="T-1", name="Temp Person"))
    database.close()
    assert path.exists() and tmp_path in path.parents
