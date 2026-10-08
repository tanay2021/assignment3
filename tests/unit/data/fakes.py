"""In-memory repository implementations for tests.

They prove the interfaces are enough to build a working implementation, and let
service tests run without SQLite.
"""

from __future__ import annotations

from typing import Optional

from src.data.repositories import (
    ApplicantRepository,
    DocumentRepository,
    LoanApplicationRepository,
)
from src.domain import Applicant, Document, LoanApplication


class InMemoryApplicantRepository(ApplicantRepository):
    def __init__(self) -> None:
        self._items: dict[str, Applicant] = {}

    def save(self, applicant: Applicant) -> None:
        self._items[applicant.applicant_id] = applicant.model_copy(deep=True)

    def get(self, applicant_id: str) -> Optional[Applicant]:
        item = self._items.get(applicant_id)
        return item.model_copy(deep=True) if item else None


class InMemoryLoanApplicationRepository(LoanApplicationRepository):
    def __init__(self) -> None:
        self._items: dict[str, LoanApplication] = {}

    def save(self, application: LoanApplication) -> None:
        self._items[application.application_id] = application.model_copy(deep=True)

    def get(self, application_id: str) -> Optional[LoanApplication]:
        item = self._items.get(application_id)
        return item.model_copy(deep=True) if item else None

    def list_by_applicant(self, applicant_id: str) -> list[LoanApplication]:
        found = [a for a in self._items.values() if a.applicant_id == applicant_id]
        return sorted(found, key=lambda a: a.application_id)


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self._items: dict[str, Document] = {}

    def save(self, document: Document) -> None:
        self._items[document.document_id] = document.model_copy(deep=True)

    def get(self, document_id: str) -> Optional[Document]:
        item = self._items.get(document_id)
        return item.model_copy(deep=True) if item else None

    def list_by_application(self, application_id: str) -> list[Document]:
        found = [d for d in self._items.values() if d.application_id == application_id]
        return sorted(found, key=lambda d: d.document_id)
