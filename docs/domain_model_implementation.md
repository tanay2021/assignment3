# Domain Model Implementation (Prompt 2)

What was built for the application foundation: the domain models, enums, validation, services, repositories and errors. Design intent is in [architecture.md](architecture.md) and [data_contracts.md](data_contracts.md); this document describes the code as it stands.

## 1. Layers and dependencies
```
app/ui  ->  app/bootstrap  ->  src/services  ->  src/data  ->  src/domain
                  |                  |               |
              app/config        src/common  <--------+---------(leaf, imports nothing)
```
- `src/` never imports `app/`. `app/bootstrap.py` reads configuration and passes plain values (the database path) down.
- `src/domain` imports only Pydantic and the standard library.
- Enforced by `tests/unit/test_architecture.py` and `tests/unit/domain/test_design_principles.py`.

## 2. Models (`src/domain/`)
All models extend `DomainModel` (`base.py`): unknown fields are rejected and strings are stripped. Money uses `Decimal`.

| Model | Purpose | Key fields |
|---|---|---|
| `Applicant` | Synthetic applicant | `applicant_id`, `name`, `date_of_birth?`, `employment_status?`, `employer?`, `annual_income?`, `other_income?`, `existing_liabilities?` (monthly) |
| `LoanApplication` | The application | `application_id`, `applicant_id`, `loan_type`, `requested_amount`, `property_value?`, `application_date`, `status` |
| `Document` | A file in the package | `document_id`, `application_id`, `document_type`, `filename`, `source_reference`, `page_count?`, `processing_status`, `status_detail?`, `metadata` |
| `DocumentEvidence` (frozen) | Source traceability | `document_id`, `page_number`, `source_reference`, `snippet?`, `field_name?`, `extracted_value?`, `section?`, `chunk_id?` |
| `ExtractedInformation` | One field with its sources | `application_id`, `field_name`, `value` (raw text), `normalized_value?`, `provenance`, `confidence?`, `evidence`, `verified_in_source`, `confirmed_by_human` |
| `PolicyDocument` | Policy metadata | `policy_id`, `title`, `version`, `effective_date?`, `source`, `metadata` |
| `PolicyQuery` (+ `ResponseRequirements`) | A policy or applicant question | `query`, `application_id?`, `requested_context`, `response_requirements` |
| `Inconsistency` | Two sources disagree | `inconsistency_id`, `application_id`, `field_name`, `source_a/value_a`, `source_b/value_b`, `description`, `severity`, `requires_human_review`, `review_status`, `reviewer_note?` |
| `UnderwritingSummary` (+ `DocumentStatusEntry`, `PolicyObservation`, `RiskIndicator`) | Case overview, data only | application, applicant, document status, financial information, inconsistencies, policy observations, risk indicators, evidence, human review items, `narrative?`, `generated_at`, `decision` |
| `AIResponse` | A grounded answer | `answer`, `evidence`, `sources`, `warnings`, `requires_human_review`, `status`, `provenance`, `generated_at` |

New loan facts (employer tenure, credit score, and so on) are new `field_name` values on `ExtractedInformation`. They do not add attributes to other models.

## 3. Enums (`enums.py`)
| Enum | Members |
|---|---|
| `DocumentType` | application, income, employment, bank_statement, property, unknown |
| `ProcessingStatus` | pending, ingested, unreadable, empty, unsupported |
| `EmploymentStatus` | salaried, self_employed, retired, unemployed, other |
| `LoanType` | home_purchase, refinance, home_equity, personal |
| `LoanStatus` | submitted, awaiting_documents, in_review, decision_recorded (a human decision recorded elsewhere; the system never sets approve or reject) |
| `InconsistencySeverity` | info, low, medium, high (assignment rules arrive with reconciliation) |
| `ReviewStatus` | open, needs_follow_up, resolved, accepted |
| `Provenance` | extracted, calculated, ai_generated |
| `Confidence` | high, medium, low (optional, set only by a defined rule) |
| `DocumentAvailability` | present, missing, unreadable |
| `QueryContext` | policy, application, policy_and_application |
| `ResponseStatus` | ok, partial, no_evidence, failed |

## 4. Validation rules (data integrity only)
| Rule | Where |
|---|---|
| IDs and required text cannot be empty or whitespace | all models |
| `requested_amount` > 0, `property_value` > 0 when given | `LoanApplication` |
| Incomes and liabilities >= 0 | `Applicant` |
| `page_number` >= 1 (pages are 1-based) | `DocumentEvidence` |
| `page_count` >= 0 | `Document` |
| Evidence needs a `snippet` or `extracted_value` | `DocumentEvidence` |
| `verified_in_source` requires evidence | `ExtractedInformation` |
| `confidence` is a qualitative enum, never a number | `ExtractedInformation` |
| Query length 1 to 1000; `max_sources` 1 to 20 | `PolicyQuery`, `ResponseRequirements` |
| Application-scoped queries need `application_id` | `PolicyQuery` |
| MEDIUM and HIGH inconsistencies must require human review | `Inconsistency` |
| OK responses need evidence; NO_EVIDENCE and FAILED must require human review | `AIResponse` |
| `decision` can only be `pending_underwriter` | `UnderwritingSummary` |
| Enum fields accept only valid members | all models |

Deliberately absent: DTI or LTV thresholds, eligibility, credit rules. Those belong to the later policy and business-rule layers.

## 5. Service boundaries (`src/services/`)
| Service | Responsibilities |
|---|---|
| `LoanApplicationService` | register and get applicants; submit and get applications; list a person's applications. An application needs a registered applicant |
| `DocumentService` | register documents (application must exist); get and list; update processing status |
| `PolicyService` | validate a policy question into a `PolicyQuery`; answering raises `PolicyError` until RAG exists |
| `UnderwritingService` | `prepare_summary`: application, applicant and document status from stored records; unreadable documents become human-review items; no calculation, AI or decision |

Rules for every service call:
- Accept only validated domain models and non-blank string ids (`_validation.py`); anything else raises `ValidationError`.
- Failures are always an `ApplicationError` subtype. Raw sqlite3, Pydantic or future provider errors are translated.
- Logs contain ids, counts and statuses only. No names, employers, income or document text.
- `create_services(database_path)` wires everything. The UI calls only this and the returned services.

## 6. Repository boundaries (`src/data/`)
- `repositories.py`: abstract `ApplicantRepository`, `LoanApplicationRepository`, `DocumentRepository` with `save` (insert or replace), `get` (record or `None`) and `list_by_*` (empty list when none).
- `sqlite.py`: `SqliteDatabase` (one connection, lock, schema creation) plus three implementations. Each entity is stored as JSON with a few lookup columns, so the domain models remain the only definition of the shape.
- Storage failures and corrupt rows raise `DataAccessError`.
- Tests run the same contract suite against an in-memory fake, in-memory SQLite and a temporary SQLite file.

## 7. Errors (`src/common/exceptions.py`)
`ApplicationError` (base), `ValidationError`, `NotFoundError`, `DocumentProcessingError`, `DataAccessError`, `PolicyError`, `ExternalServiceError`. `user_message` is safe to show; for data and external-service errors it hides technical detail.

## 8. Configuration and logging
- `app/config.py` is the only place environment variables are read. `DATABASE_PATH` (default `data/loan_poc.sqlite3`, `:memory:` for tests) was added there.
- Logging uses `app/logging_config.py`; modules log through child loggers of `loan_processing_ai_poc`.
- Nothing in the foundation needs an OpenAI key.

## 9. Design decisions
See ADR-013, ADR-014 and ADR-015 in [architecture_decisions.md](architecture_decisions.md). In short: Pydantic models, JSON-document SQLite repositories without an ORM, typed errors instead of a result object for now, a single wiring function, and `src/` independent of `app/`.

## 10. Test map
| Area | Location |
|---|---|
| Models, validation, enums, boundaries | `tests/unit/domain/` |
| Design principles and layering | `tests/unit/domain/test_design_principles.py`, `tests/unit/test_architecture.py` |
| Errors | `tests/unit/common/` |
| Repositories (contract plus SQLite specifics) | `tests/unit/data/` |
| Services and boundaries | `tests/unit/services/` |
| Configuration, bootstrap | `tests/unit/test_config_database.py`, `tests/unit/test_application_bootstrap.py` |
| Environment health | `tests/unit/test_foundation.py`, `tests/integration/` |
