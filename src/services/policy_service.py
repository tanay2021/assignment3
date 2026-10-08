"""Application boundary for policy questions (foundation only)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from pydantic import ValidationError as PydanticValidationError

from src.common.exceptions import PolicyError, ValidationError
from src.domain import AIResponse, PolicyQuery
from src.domain.enums import QueryContext
from src.services._validation import require_enum, require_model

logger = logging.getLogger("loan_processing_ai_poc.services.policy")


class PolicyService:
    """Validates policy questions. Answering them arrives with the RAG layer."""

    def create_query(
        self,
        question: Any,
        application_id: Optional[str] = None,
        context: QueryContext = QueryContext.POLICY,
    ) -> PolicyQuery:
        context = require_enum(context, QueryContext, "context")
        try:
            return PolicyQuery(
                query=question, application_id=application_id, requested_context=context
            )
        except PydanticValidationError as exc:
            raise ValidationError("The question is not valid: " + _first_message(exc)) from exc

    def answer(self, query: PolicyQuery) -> AIResponse:
        require_model(query, PolicyQuery, "query")
        logger.info("Policy answering requested but not available yet")
        raise PolicyError("Policy question answering is not available yet.")


def _first_message(exc: PydanticValidationError) -> str:
    errors = exc.errors()
    return str(errors[0]["msg"]) if errors else "invalid input"
