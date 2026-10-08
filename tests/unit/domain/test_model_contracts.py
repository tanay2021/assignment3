"""Table-driven checks over every domain model: missing values, enums, boundaries.

Deterministic, fast and offline. Only ``src.domain`` and the standard library are used.
"""

from __future__ import annotations

import inspect
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import pytest
from pydantic import ValidationError

from src.domain import (
    AIResponse,
    Applicant,
    Document,
    DocumentEvidence,
    ExtractedInformation,
    Inconsistency,
    LoanApplication,
    PolicyDocument,
    PolicyQuery,
    ResponseRequirements,
    UnderwritingSummary,
)
from src.domain import enums
from src.domain.enums import (
    DocumentType,
    EmploymentStatus,
    InconsistencySeverity,
    LoanType,
    ProcessingStatus,
    ResponseStatus,
)

EVIDENCE_A = DocumentEvidence(
    document_id="DOC-001", page_number=1, source_reference="a.pdf", snippet="Income $120,000"
)
EVIDENCE_B = DocumentEvidence(
    document_id="DOC-002", page_number=2, source_reference="b.pdf", snippet="Income $105,000"
)
APPLICANT = Applicant(applicant_id="APP-001", name="Jordan Sample")
APPLICATION = LoanApplication(
    application_id="LOAN-001",
    applicant_id="APP-001",
    loan_type=LoanType.HOME_PURCHASE,
    requested_amount=Decimal("100000"),
    application_date=date(2026, 1, 1),
)

# model class -> (function returning valid kwargs, required field names)
CASES: dict[str, tuple[type, Callable[[], dict[str, Any]], list[str]]] = {
    "Applicant": (
        Applicant,
        lambda: dict(applicant_id="APP-001", name="Jordan Sample"),
        ["applicant_id", "name"],
    ),
    "LoanApplication": (
        LoanApplication,
        lambda: dict(
            application_id="LOAN-001",
            applicant_id="APP-001",
            loan_type="home_purchase",
            requested_amount="100000",
            application_date="2026-01-01",
        ),
        ["application_id", "applicant_id", "loan_type", "requested_amount", "application_date"],
    ),
    "Document": (
        Document,
        lambda: dict(
            document_id="DOC-1",
            application_id="LOAN-001",
            document_type="income",
            filename="slip.pdf",
            source_reference="data/slip.pdf",
        ),
        ["document_id", "application_id", "document_type", "filename", "source_reference"],
    ),
    "DocumentEvidence": (
        DocumentEvidence,
        lambda: dict(document_id="DOC-1", page_number=1, source_reference="a.pdf", snippet="x"),
        ["document_id", "page_number", "source_reference"],
    ),
    "ExtractedInformation": (
        ExtractedInformation,
        lambda: dict(application_id="LOAN-001", field_name="annual_income", value="120000"),
        ["application_id", "field_name", "value"],
    ),
    "PolicyDocument": (
        PolicyDocument,
        lambda: dict(policy_id="POL-1", title="Policy", version="2025.1", source="policy.pdf"),
        ["policy_id", "title", "version", "source"],
    ),
    "PolicyQuery": (PolicyQuery, lambda: dict(query="What is the maximum DTI?"), ["query"]),
    "Inconsistency": (
        Inconsistency,
        lambda: dict(
            inconsistency_id="INC-1",
            application_id="LOAN-001",
            field_name="annual_income",
            source_a=EVIDENCE_A,
            value_a="120000",
            source_b=EVIDENCE_B,
            value_b="105000",
            description="Income differs.",
            severity="high",
        ),
        [
            "inconsistency_id",
            "application_id",
            "field_name",
            "source_a",
            "value_a",
            "source_b",
            "value_b",
            "description",
            "severity",
        ],
    ),
    "UnderwritingSummary": (
        UnderwritingSummary,
        lambda: dict(application=APPLICATION, applicant=APPLICANT),
        ["application", "applicant"],
    ),
    "AIResponse": (
        AIResponse,
        lambda: dict(answer="43%", evidence=[EVIDENCE_A]),
        ["answer"],
    ),
}


@pytest.mark.parametrize("name", CASES)
def test_valid_baseline_builds(name: str) -> None:
    model, build, _ = CASES[name]
    assert model(**build()) is not None


@pytest.mark.parametrize(
    "name,field",
    [(name, field) for name, (_, _, required) in CASES.items() for field in required],
)
def test_missing_required_value_is_rejected(name: str, field: str) -> None:
    model, build, _ = CASES[name]
    data = build()
    del data[field]
    with pytest.raises(ValidationError) as info:
        model(**data)
    assert any(error["loc"] == (field,) for error in info.value.errors())


@pytest.mark.parametrize("name", CASES)
def test_unknown_fields_are_rejected(name: str) -> None:
    model, build, _ = CASES[name]
    with pytest.raises(ValidationError):
        model(**build(), surprise_field="x")


@pytest.mark.parametrize("name", CASES)
def test_models_round_trip_through_json(name: str) -> None:
    model, build, _ = CASES[name]
    original = model(**build())
    assert model.model_validate_json(original.model_dump_json()) == original


@pytest.mark.parametrize(
    "name,field",
    [
        ("Applicant", "applicant_id"),
        ("Applicant", "name"),
        ("LoanApplication", "application_id"),
        ("Document", "filename"),
        ("DocumentEvidence", "source_reference"),
        ("ExtractedInformation", "field_name"),
        ("PolicyDocument", "title"),
        ("PolicyDocument", "version"),
        ("Inconsistency", "description"),
    ],
)
@pytest.mark.parametrize("empty", ["", "   ", "\t\n"])
def test_blank_required_text_is_rejected(name: str, field: str, empty: str) -> None:
    model, build, _ = CASES[name]
    data = build()
    data[field] = empty
    with pytest.raises(ValidationError):
        model(**data)


def test_text_is_stripped() -> None:
    applicant = Applicant(applicant_id="  APP-9  ", name=" Casey Example ")
    assert (applicant.applicant_id, applicant.name) == ("APP-9", "Casey Example")


# ---------------------------------------------------------------- enums


ENUM_CLASSES = [
    cls
    for _, cls in inspect.getmembers(enums, inspect.isclass)
    if issubclass(cls, enums.Enum) and cls.__module__ == enums.__name__
]


@pytest.mark.parametrize("enum_cls", ENUM_CLASSES, ids=lambda c: c.__name__)
def test_every_enum_is_a_unique_lowercase_string_vocabulary(enum_cls: type) -> None:
    values = [member.value for member in enum_cls]
    assert values and len(values) == len(set(values))
    assert all(isinstance(v, str) and v == v.lower() and " " not in v for v in values)
    for member in enum_cls:
        assert enum_cls(member.value) is member
    with pytest.raises(ValueError):
        enum_cls("not_a_member")


def test_required_enums_exist_with_expected_members() -> None:
    assert {m.name for m in InconsistencySeverity} == {"INFO", "LOW", "MEDIUM", "HIGH"}
    assert {m.name for m in ProcessingStatus} >= {"PENDING", "INGESTED", "UNREADABLE", "EMPTY"}
    assert {m.name for m in DocumentType} >= {"APPLICATION", "INCOME", "BANK_STATEMENT"}
    assert {m.name for m in EmploymentStatus} >= {"SALARIED", "SELF_EMPLOYED"}
    assert {m.name for m in enums.LoanStatus} >= {"SUBMITTED", "IN_REVIEW", "DECISION_RECORDED"}


def test_no_enum_encodes_an_automated_decision() -> None:
    banned = {"approved", "rejected", "approve", "reject", "declined"}
    for enum_cls in ENUM_CLASSES:
        assert not banned & {m.value for m in enum_cls}, enum_cls.__name__


@pytest.mark.parametrize(
    "name,field",
    [
        ("Applicant", "employment_status"),
        ("LoanApplication", "loan_type"),
        ("LoanApplication", "status"),
        ("Document", "document_type"),
        ("Document", "processing_status"),
        ("Inconsistency", "severity"),
        ("Inconsistency", "review_status"),
        ("PolicyQuery", "requested_context"),
        ("AIResponse", "status"),
    ],
)
def test_invalid_enum_value_is_rejected_by_models(name: str, field: str) -> None:
    model, build, _ = CASES[name]
    data = build()
    data[field] = "definitely_invalid"
    with pytest.raises(ValidationError):
        model(**data)


def test_enum_members_and_their_strings_are_both_accepted() -> None:
    from_string = Document(**{**CASES["Document"][1](), "document_type": "bank_statement"})
    from_member = Document(
        **{**CASES["Document"][1](), "document_type": DocumentType.BANK_STATEMENT}
    )
    assert from_string.document_type is from_member.document_type


# ------------------------------------------------- boundaries and negatives


@pytest.mark.parametrize("amount,ok", [("0.01", True), ("1", True), ("0", False), ("-0.01", False)])
def test_requested_amount_boundary(amount: str, ok: bool) -> None:
    data = {**CASES["LoanApplication"][1](), "requested_amount": amount}
    if ok:
        assert LoanApplication(**data).requested_amount == Decimal(amount)
    else:
        with pytest.raises(ValidationError):
            LoanApplication(**data)


@pytest.mark.parametrize("value,ok", [("0.01", True), ("0", False), ("-1", False)])
def test_property_value_boundary(value: str, ok: bool) -> None:
    data = {**CASES["LoanApplication"][1](), "property_value": value}
    if ok:
        LoanApplication(**data)
    else:
        with pytest.raises(ValidationError):
            LoanApplication(**data)


@pytest.mark.parametrize("field", ["annual_income", "other_income", "existing_liabilities"])
@pytest.mark.parametrize("value,ok", [("0", True), ("0.01", True), ("-0.01", False), ("-1000", False)])
def test_applicant_money_boundaries(field: str, value: str, ok: bool) -> None:
    data = {**CASES["Applicant"][1](), field: value}
    if ok:
        assert getattr(Applicant(**data), field) == Decimal(value)
    else:
        with pytest.raises(ValidationError):
            Applicant(**data)


def test_money_accepts_very_large_values_without_rounding() -> None:
    applicant = Applicant(**{**CASES["Applicant"][1](), "annual_income": "99999999999.99"})
    assert applicant.annual_income == Decimal("99999999999.99")


@pytest.mark.parametrize("page,ok", [(1, True), (2, True), (0, False), (-1, False)])
def test_evidence_page_boundary(page: int, ok: bool) -> None:
    data = {**CASES["DocumentEvidence"][1](), "page_number": page}
    if ok:
        assert DocumentEvidence(**data).page_number == page
    else:
        with pytest.raises(ValidationError):
            DocumentEvidence(**data)


@pytest.mark.parametrize("count,ok", [(0, True), (1, True), (500, True), (-1, False)])
def test_document_page_count_boundary(count: int, ok: bool) -> None:
    data = {**CASES["Document"][1](), "page_count": count}
    if ok:
        assert Document(**data).page_count == count
    else:
        with pytest.raises(ValidationError):
            Document(**data)


@pytest.mark.parametrize("length,ok", [(1, True), (1000, True), (1001, False)])
def test_query_length_boundary(length: int, ok: bool) -> None:
    if ok:
        assert len(PolicyQuery(query="q" * length).query) == length
    else:
        with pytest.raises(ValidationError):
            PolicyQuery(query="q" * length)


@pytest.mark.parametrize("sources,ok", [(1, True), (20, True), (0, False), (21, False)])
def test_max_sources_boundary(sources: int, ok: bool) -> None:
    if ok:
        assert ResponseRequirements(max_sources=sources).max_sources == sources
    else:
        with pytest.raises(ValidationError):
            ResponseRequirements(max_sources=sources)


# ------------------------------------------------ model-specific validation


def test_policy_document_rejects_bad_date_and_nested_metadata() -> None:
    base = CASES["PolicyDocument"][1]()
    PolicyDocument(**base, effective_date="2025-01-31")
    with pytest.raises(ValidationError):
        PolicyDocument(**base, effective_date="31/31/2025")
    with pytest.raises(ValidationError):
        PolicyDocument(**base, metadata={"nested": {"a": 1}})


def test_extracted_information_normalized_variants_and_missing_value() -> None:
    base = dict(application_id="L", field_name="f", value="raw")
    for normalized in (Decimal("1.5"), date(2026, 1, 1), True):
        info = ExtractedInformation(**base, normalized_value=normalized)
        assert info.normalized_value == normalized
        assert ExtractedInformation.model_validate_json(info.model_dump_json()) == info
    with pytest.raises(ValidationError):
        ExtractedInformation(application_id="L", field_name="f", value=None)


@pytest.mark.parametrize("raw", ["120000", "2026-01-01", "true", "$120,000", "007"])
def test_raw_value_text_survives_json_round_trip_unchanged(raw: str) -> None:
    info = ExtractedInformation(application_id="L", field_name="f", value=raw)
    restored = ExtractedInformation.model_validate_json(info.model_dump_json())
    assert restored.value == raw and isinstance(restored.value, str)


def test_inconsistency_review_rules_cover_every_severity() -> None:
    base = CASES["Inconsistency"][1]()
    for severity in InconsistencySeverity:
        serious = severity in (InconsistencySeverity.MEDIUM, InconsistencySeverity.HIGH)
        data = {**base, "severity": severity, "requires_human_review": False}
        if serious:
            with pytest.raises(ValidationError):
                Inconsistency(**data)
        else:
            assert Inconsistency(**data).requires_human_review is False


def test_summary_rejects_invalid_nested_models_and_decisions() -> None:
    base = CASES["UnderwritingSummary"][1]()
    with pytest.raises(ValidationError):
        UnderwritingSummary(**{**base, "applicant": {"applicant_id": "", "name": "X"}})
    with pytest.raises(ValidationError):
        UnderwritingSummary(**{**base, "decision": "approved"})
    with pytest.raises(ValidationError):
        UnderwritingSummary(**{**base, "document_status": [{"document_type": "income"}]})


def test_ai_response_status_rules_cover_every_status() -> None:
    for status in ResponseStatus:
        data = dict(answer="text", status=status)
        needs_evidence = status is ResponseStatus.OK
        needs_review = status in (ResponseStatus.NO_EVIDENCE, ResponseStatus.FAILED)
        if needs_evidence:
            with pytest.raises(ValidationError):
                AIResponse(**data, requires_human_review=True)
        if needs_review:
            with pytest.raises(ValidationError):
                AIResponse(**data)
            assert AIResponse(**data, requires_human_review=True).evidence == []


def test_ai_response_keeps_answer_evidence_and_warnings_separate() -> None:
    fields = AIResponse.model_fields
    assert {"answer", "evidence", "warnings"} <= set(fields)
    response = AIResponse(answer="A", evidence=[EVIDENCE_A], warnings=["W"])
    assert "W" not in response.answer


# ------------------------------------------------------------ independence


def test_domain_package_loads_without_ai_or_vector_libraries() -> None:
    """Import src.domain in a clean interpreter and check nothing heavy was loaded."""
    code = (
        "import sys, src.domain;"
        "heavy = {'openai','chromadb','langchain','sentence_transformers','streamlit'};"
        "loaded = heavy & {m.split('.')[0] for m in sys.modules};"
        "sys.exit(1 if loaded else 0)"
    )
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
