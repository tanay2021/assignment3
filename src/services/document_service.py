"""Application use cases for loan documents (records only, no processing yet)."""

from __future__ import annotations

import logging
from typing import Optional

from src.common.exceptions import NotFoundError
from src.data.repositories import DocumentRepository, LoanApplicationRepository
from src.domain import Document
from src.domain.enums import ProcessingStatus
from src.services._validation import require_enum, require_id, require_model

logger = logging.getLogger("loan_processing_ai_poc.services.document")


class DocumentService:
    """Tracks which documents belong to an application and their processing status.

    Reading and extracting documents belongs to the future document intelligence layer.
    """

    def __init__(
        self, documents: DocumentRepository, applications: LoanApplicationRepository
    ) -> None:
        self._documents = documents
        self._applications = applications

    def register_document(self, document: Document) -> Document:
        require_model(document, Document, "document")
        if self._applications.get(document.application_id) is None:
            raise NotFoundError(f"Application {document.application_id} was not found.")
        self._documents.save(document)
        logger.info(
            "Registered document %s (%s) for application %s",
            document.document_id,
            document.document_type.value,
            document.application_id,
        )
        return document

    def get_document(self, document_id: str) -> Document:
        document_id = require_id(document_id, "document_id")
        document = self._documents.get(document_id)
        if document is None:
            raise NotFoundError(f"Document {document_id} was not found.")
        return document

    def list_documents(self, application_id: str) -> list[Document]:
        application_id = require_id(application_id, "application_id")
        return self._documents.list_by_application(application_id)

    def update_processing_status(
        self, document_id: str, status: ProcessingStatus, detail: Optional[str] = None
    ) -> Document:
        status = require_enum(status, ProcessingStatus, "status")
        current = self.get_document(document_id)
        updated = Document.model_validate(
            {**current.model_dump(), "processing_status": status, "status_detail": detail}
        )
        self._documents.save(updated)
        logger.info("Document %s status -> %s", current.document_id, status.value)
        return updated
