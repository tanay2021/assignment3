"""Application boundary for underwriting review (foundation only)."""

from __future__ import annotations

import logging

from src.common.exceptions import NotFoundError
from src.data.repositories import (
    ApplicantRepository,
    DocumentRepository,
    LoanApplicationRepository,
)
from src.domain import DocumentStatusEntry, UnderwritingSummary
from src.domain.enums import DocumentAvailability, ProcessingStatus
from src.services._validation import require_id

logger = logging.getLogger("loan_processing_ai_poc.services.underwriting")

_UNREADABLE = {
    ProcessingStatus.UNREADABLE,
    ProcessingStatus.EMPTY,
    ProcessingStatus.UNSUPPORTED,
}


class UnderwritingService:
    """Assembles the starting point of an underwriting summary from stored records.

    It performs no extraction, calculation, policy checking or AI generation and
    never records a decision. Those capabilities are added by later layers.
    """

    def __init__(
        self,
        applications: LoanApplicationRepository,
        applicants: ApplicantRepository,
        documents: DocumentRepository,
    ) -> None:
        self._applications = applications
        self._applicants = applicants
        self._documents = documents

    def prepare_summary(self, application_id: str) -> UnderwritingSummary:
        application_id = require_id(application_id, "application_id")
        application = self._applications.get(application_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} was not found.")
        applicant = self._applicants.get(application.applicant_id)
        if applicant is None:
            raise NotFoundError(f"Applicant {application.applicant_id} was not found.")

        entries: list[DocumentStatusEntry] = []
        review_items: list[str] = []
        for document in self._documents.list_by_application(application_id):
            unreadable = document.processing_status in _UNREADABLE
            entries.append(
                DocumentStatusEntry(
                    document_type=document.document_type,
                    availability=(
                        DocumentAvailability.UNREADABLE if unreadable else DocumentAvailability.PRESENT
                    ),
                    document_id=document.document_id,
                    detail=document.status_detail,
                )
            )
            if unreadable:
                review_items.append(f"Document {document.document_id} could not be read.")

        logger.info(
            "Prepared summary skeleton for application %s with %d documents",
            application_id,
            len(entries),
        )
        return UnderwritingSummary(
            application=application,
            applicant=applicant,
            document_status=entries,
            human_review_items=review_items,
        )
