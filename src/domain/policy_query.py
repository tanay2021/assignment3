"""Policy query contract."""

from __future__ import annotations

from typing import Optional

from pydantic import Field, model_validator

from src.domain.base import DomainModel
from src.domain.enums import QueryContext

MAX_QUERY_LENGTH = 1000


class ResponseRequirements(DomainModel):
    """What the caller needs from the answer. Enforced by later layers."""

    require_citations: bool = True
    allow_no_answer: bool = True
    max_sources: int = Field(default=5, ge=1, le=20)


class PolicyQuery(DomainModel):
    """A validated question for the policy assistant."""

    query: str = Field(min_length=1, max_length=MAX_QUERY_LENGTH)
    application_id: Optional[str] = None
    requested_context: QueryContext = QueryContext.POLICY
    response_requirements: ResponseRequirements = Field(default_factory=ResponseRequirements)

    @model_validator(mode="after")
    def _application_context_needs_id(self) -> "PolicyQuery":
        needs_application = self.requested_context in (
            QueryContext.APPLICATION,
            QueryContext.POLICY_AND_APPLICATION,
        )
        if needs_application and not self.application_id:
            raise ValueError("application_id is required when the context includes the application.")
        return self
