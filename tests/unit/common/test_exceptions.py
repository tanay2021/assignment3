"""Tests for the lightweight application exception hierarchy."""

from __future__ import annotations

import pytest

from src.common import (
    ApplicationError,
    DataAccessError,
    DocumentProcessingError,
    ExternalServiceError,
    NotFoundError,
    PolicyError,
    ValidationError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        ValidationError,
        NotFoundError,
        DocumentProcessingError,
        DataAccessError,
        PolicyError,
        ExternalServiceError,
    ],
)
def test_all_errors_share_one_base(error_type: type[ApplicationError]) -> None:
    with pytest.raises(ApplicationError):
        raise error_type("boom")


def test_user_message_defaults_to_message() -> None:
    assert NotFoundError("Application X was not found.").user_message == "Application X was not found."


def test_provider_details_never_reach_user_message() -> None:
    raw = "openai.AuthenticationError: invalid key sk-secret"
    assert "sk-secret" not in ExternalServiceError(raw).user_message
    assert "sqlite3" not in DataAccessError("sqlite3.OperationalError: disk I/O").user_message


def test_original_cause_is_chained() -> None:
    try:
        try:
            raise RuntimeError("provider failure")
        except RuntimeError as exc:
            raise ExternalServiceError("LLM call failed") from exc
    except ExternalServiceError as err:
        assert isinstance(err.__cause__, RuntimeError)
