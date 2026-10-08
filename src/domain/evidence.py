"""Document evidence: the link from any derived information back to its source."""

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field, model_validator

from src.domain.base import DomainModel


class DocumentEvidence(DomainModel):
    """A pointer to the exact place in a document that supports a value or answer."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    document_id: str = Field(min_length=1)
    page_number: int = Field(ge=1, description="1-based page number.")
    source_reference: str = Field(min_length=1, description="Human-readable source, e.g. a filename.")
    snippet: Optional[str] = Field(default=None, description="Exact text from the page.")
    field_name: Optional[str] = None
    extracted_value: Optional[str] = None
    section: Optional[str] = None
    chunk_id: Optional[str] = None

    @model_validator(mode="after")
    def _require_content(self) -> "DocumentEvidence":
        if not self.snippet and not self.extracted_value:
            raise ValueError("Evidence needs a snippet or an extracted_value.")
        return self
