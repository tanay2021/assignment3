"""Application-level exceptions.

Lower layers translate library errors (sqlite3, Pydantic, future OpenAI errors)
into these types so callers and the UI never see raw provider exceptions.

Note: ``ValidationError`` here is the application's error. Pydantic has one with
the same name; import Pydantic's as ``from pydantic import ValidationError as PydanticValidationError``
where both are needed.
"""

from __future__ import annotations


class ApplicationError(Exception):
    """Base class for every error the application raises deliberately."""

    #: Safe text for end users. When set, it replaces the technical message in the UI.
    default_user_message: str | None = None

    @property
    def user_message(self) -> str:
        return self.default_user_message or str(self)


class ValidationError(ApplicationError):
    """Input or data failed domain validation. The message is safe to show."""


class NotFoundError(ApplicationError):
    """A requested record does not exist."""


class DocumentProcessingError(ApplicationError):
    """A document could not be read or processed (unreadable, empty, unsupported)."""


class DataAccessError(ApplicationError):
    """The data store failed or returned unusable data."""

    default_user_message = "The data store could not complete the request. Please try again."


class PolicyError(ApplicationError):
    """Policy lookup or policy question handling failed or is unavailable."""


class ExternalServiceError(ApplicationError):
    """An external AI or API service failed. Provider details stay in the log, not the UI."""

    default_user_message = "The AI service is unavailable right now. Please try again later."
