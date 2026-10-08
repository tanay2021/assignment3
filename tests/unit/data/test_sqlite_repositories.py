"""SQLite repositories: round trips, listing, replacement and error translation."""

from __future__ import annotations

from decimal import Decimal

import pytest

from src.common.exceptions import DataAccessError
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


@pytest.fixture
def database():
    db = SqliteDatabase(":memory:")
    yield db
    db.close()


def test_implementations_satisfy_the_interfaces(database: SqliteDatabase) -> None:
    assert isinstance(SqliteApplicantRepository(database), ApplicantRepository)
    assert isinstance(SqliteLoanApplicationRepository(database), LoanApplicationRepository)
    assert isinstance(SqliteDocumentRepository(database), DocumentRepository)


def test_applicant_round_trip_keeps_decimal_values(
    database: SqliteDatabase, applicant: Applicant
) -> None:
    repo = SqliteApplicantRepository(database)
    repo.save(applicant)
    loaded = repo.get("APP-001")
    assert loaded == applicant
    assert loaded.annual_income == Decimal("120000")


def test_missing_records_return_none_or_empty(database: SqliteDatabase) -> None:
    assert SqliteApplicantRepository(database).get("nope") is None
    assert SqliteLoanApplicationRepository(database).get("nope") is None
    assert SqliteLoanApplicationRepository(database).list_by_applicant("nope") == []
    assert SqliteDocumentRepository(database).list_by_application("nope") == []


def test_save_replaces_existing_record(
    database: SqliteDatabase, application: LoanApplication
) -> None:
    repo = SqliteLoanApplicationRepository(database)
    repo.save(application)
    repo.save(application.model_copy(update={"requested_amount": Decimal("250000")}))
    assert repo.get("LOAN-001").requested_amount == Decimal("250000")
    assert len(repo.list_by_applicant("APP-001")) == 1


def test_documents_are_listed_per_application(database: SqliteDatabase, document: Document) -> None:
    repo = SqliteDocumentRepository(database)
    repo.save(document)
    repo.save(document.model_copy(update={"document_id": "DOC-002"}))
    repo.save(document.model_copy(update={"document_id": "DOC-003", "application_id": "LOAN-999"}))
    assert [d.document_id for d in repo.list_by_application("LOAN-001")] == ["DOC-001", "DOC-002"]


def test_data_persists_in_a_file_database(tmp_path, applicant: Applicant) -> None:
    path = str(tmp_path / "nested" / "poc.sqlite3")
    first = SqliteDatabase(path)
    SqliteApplicantRepository(first).save(applicant)
    first.close()
    second = SqliteDatabase(path)
    assert SqliteApplicantRepository(second).get("APP-001") == applicant
    second.close()


def test_storage_failure_becomes_data_access_error(
    database: SqliteDatabase, applicant: Applicant
) -> None:
    repo = SqliteApplicantRepository(database)
    database.close()
    with pytest.raises(DataAccessError) as info:
        repo.save(applicant)
    assert "sqlite" not in info.value.user_message.lower()


def test_corrupt_stored_record_becomes_data_access_error(database: SqliteDatabase) -> None:
    database.execute(
        "INSERT INTO applicants (applicant_id, data) VALUES (?, ?)", ("BAD", '{"applicant_id": ""}')
    )
    with pytest.raises(DataAccessError):
        SqliteApplicantRepository(database).get("BAD")


def test_unopenable_database_becomes_data_access_error(tmp_path) -> None:
    blocker = tmp_path / "file.txt"
    blocker.write_text("x")
    with pytest.raises(DataAccessError):
        SqliteDatabase(str(blocker / "db.sqlite3"))
