"""Composition root: builds the services from configuration.

The UI calls ``create_services`` and uses the returned services only. It never
touches repositories, SQLite or domain rules directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.data import (
    SqliteApplicantRepository,
    SqliteDatabase,
    SqliteDocumentRepository,
    SqliteLoanApplicationRepository,
)
from src.services.document_service import DocumentService
from src.services.loan_application_service import LoanApplicationService
from src.services.policy_service import PolicyService
from src.services.underwriting_service import UnderwritingService


@dataclass(frozen=True)
class Services:
    loan_applications: LoanApplicationService
    documents: DocumentService
    policies: PolicyService
    underwriting: UnderwritingService
    database: SqliteDatabase


def create_services(database_path: str) -> Services:
    """Wire repositories and services for the given SQLite location.

    The caller (``app.bootstrap``) resolves the path from configuration, so this
    layer never reads settings itself. Works without an OpenAI API key.
    """
    database = SqliteDatabase(database_path)
    applicants = SqliteApplicantRepository(database)
    applications = SqliteLoanApplicationRepository(database)
    documents = SqliteDocumentRepository(database)
    return Services(
        loan_applications=LoanApplicationService(applicants, applications),
        documents=DocumentService(documents, applications),
        policies=PolicyService(),
        underwriting=UnderwritingService(applications, applicants, documents),
        database=database,
    )
