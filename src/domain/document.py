"""Document contract for loan package files."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from src.domain.base import DomainModel
from src.domain.enums import DocumentType, ProcessingStatus

MetadataValue = str | int | float | bool | None


class Document(DomainModel):
    """A file in a loan package and its processing status."""

    document_id: str = Field(min_length=1)
    application_id: str = Field(min_length=1)
    document_type: DocumentType
    filename: str = Field(min_length=1)
    source_reference: str = Field(min_length=1, description="File path or other locator of the source file.")
    page_count: Optional[int] = Field(default=None, ge=0)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    status_detail: Optional[str] = Field(default=None, description="Reason when not ingested.")
    ingested_at: Optional[datetime] = None
    metadata: dict[str, MetadataValue] = Field(default_factory=dict)
