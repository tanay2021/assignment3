"""Data access layer: repository interfaces and their SQLite implementation."""

from src.data.repositories import (
    ApplicantRepository,
    DocumentRepository,
    LoanApplicationRepository,
)
from src.data.sqlite import (
    SqliteApplicantRepository,
    SqliteDatabase,
    SqliteDocumentRepository,
    SqliteLoanApplicationRepository,
)

__all__ = [
    "ApplicantRepository",
    "DocumentRepository",
    "LoanApplicationRepository",
    "SqliteApplicantRepository",
    "SqliteDatabase",
    "SqliteDocumentRepository",
    "SqliteLoanApplicationRepository",
]
