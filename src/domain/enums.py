"""Controlled vocabularies shared across the application."""

from __future__ import annotations

from enum import Enum


class EmploymentStatus(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    UNEMPLOYED = "unemployed"
    OTHER = "other"


class LoanType(str, Enum):
    HOME_PURCHASE = "home_purchase"
    REFINANCE = "refinance"
    HOME_EQUITY = "home_equity"
    PERSONAL = "personal"


class LoanStatus(str, Enum):
    """Workflow status of an application.

    DECISION_RECORDED means a human underwriter recorded a decision outside this
    system. The application never sets an approval or rejection itself.
    """

    SUBMITTED = "submitted"
    AWAITING_DOCUMENTS = "awaiting_documents"
    IN_REVIEW = "in_review"
    DECISION_RECORDED = "decision_recorded"


class DocumentType(str, Enum):
    APPLICATION = "application"
    INCOME = "income"
    EMPLOYMENT = "employment"
    BANK_STATEMENT = "bank_statement"
    PROPERTY = "property"
    UNKNOWN = "unknown"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    INGESTED = "ingested"
    UNREADABLE = "unreadable"
    EMPTY = "empty"
    UNSUPPORTED = "unsupported"


class DocumentAvailability(str, Enum):
    """Outcome of the completeness check for one expected document type."""

    PRESENT = "present"
    MISSING = "missing"
    UNREADABLE = "unreadable"


class Provenance(str, Enum):
    """How a piece of information was produced."""

    EXTRACTED = "extracted"
    CALCULATED = "calculated"
    AI_GENERATED = "ai_generated"


class InconsistencySeverity(str, Enum):
    """Controlled severity scale. Assignment rules are implemented later in code."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewStatus(str, Enum):
    OPEN = "open"
    NEEDS_FOLLOW_UP = "needs_follow_up"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class Confidence(str, Enum):
    """Qualitative confidence. Only set when a defined rule justifies it."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class QueryContext(str, Enum):
    POLICY = "policy"
    APPLICATION = "application"
    POLICY_AND_APPLICATION = "policy_and_application"


class ResponseStatus(str, Enum):
    OK = "ok"
    PARTIAL = "partial"
    NO_EVIDENCE = "no_evidence"
    FAILED = "failed"
