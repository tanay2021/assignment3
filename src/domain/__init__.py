"""Shared domain contracts. This package imports nothing from the rest of the project."""

from src.domain.ai_response import AIResponse
from src.domain.applicant import Applicant
from src.domain.document import Document
from src.domain.evidence import DocumentEvidence
from src.domain.extracted_information import ExtractedInformation
from src.domain.inconsistency import Inconsistency
from src.domain.loan_application import LoanApplication
from src.domain.policy import PolicyDocument
from src.domain.policy_query import PolicyQuery, ResponseRequirements
from src.domain.underwriting_summary import (
    DocumentStatusEntry,
    PolicyObservation,
    RiskIndicator,
    UnderwritingSummary,
)

__all__ = [
    "AIResponse",
    "Applicant",
    "Document",
    "DocumentEvidence",
    "DocumentStatusEntry",
    "ExtractedInformation",
    "Inconsistency",
    "LoanApplication",
    "PolicyDocument",
    "PolicyObservation",
    "PolicyQuery",
    "ResponseRequirements",
    "RiskIndicator",
    "UnderwritingSummary",
]
