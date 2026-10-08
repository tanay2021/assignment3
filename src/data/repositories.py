"""Repository interfaces: what services may ask of persistence.

Services depend on these abstractions only. Implementations live elsewhere
(``src.data.sqlite``) and can be swapped without touching service code.
Implementations raise ``DataAccessError`` for storage failures and return
``None`` or an empty list when a record simply does not exist.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.domain import Applicant, Document, LoanApplication


class ApplicantRepository(ABC):
    @abstractmethod
    def save(self, applicant: Applicant) -> None:
        """Insert or replace an applicant."""

    @abstractmethod
    def get(self, applicant_id: str) -> Optional[Applicant]:
        """Return the applicant or None."""


class LoanApplicationRepository(ABC):
    @abstractmethod
    def save(self, application: LoanApplication) -> None:
        """Insert or replace a loan application."""

    @abstractmethod
    def get(self, application_id: str) -> Optional[LoanApplication]:
        """Return the application or None."""

    @abstractmethod
    def list_by_applicant(self, applicant_id: str) -> list[LoanApplication]:
        """Return all applications of one applicant."""


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> None:
        """Insert or replace a document record."""

    @abstractmethod
    def get(self, document_id: str) -> Optional[Document]:
        """Return the document or None."""

    @abstractmethod
    def list_by_application(self, application_id: str) -> list[Document]:
        """Return all documents of one application."""
