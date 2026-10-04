# Data Contracts (logical)

Logical schemas only. Prompt 2 converts them into Python models in `src/domain/` (dataclasses or similar, no new dependency). Types are indicative. `?` means optional.

## Shared enums
- `DocumentType`: application, income, employment, bank_statement, property, policy, unknown
- `DocumentStatus`: ingested, unreadable, empty, unsupported
- `Provenance`: extracted | calculated | ai_generated
- `Severity`: low, medium, high
- `ReviewStatus`: open, needs_follow_up, resolved, accepted
- `Confidence`: high, medium, low (qualitative, not a numeric probability)

## A. LoanApplication
| Field | Type | Note |
|---|---|---|
| loan_id | str | e.g. LOAN-001 |
| applicant_id | str | link to Applicant |
| loan_amount | decimal | |
| loan_purpose | str | |
| term_months | int? | |
| property_value | decimal? | |
| stated_annual_income | decimal? | value declared on the application |
| document_ids | list[str] | |
| created_at | datetime | |

## B. Applicant
| Field | Type | Note |
|---|---|---|
| applicant_id | str | synthetic id |
| full_name | str | synthetic name |
| employment_type | enum? | salaried / self_employed |
| employer_name | str? | |
| existing_monthly_liabilities | decimal? | |

## C. Document
| Field | Type | Note |
|---|---|---|
| document_id | str | |
| loan_id | str? | null for policy documents |
| document_type | DocumentType | |
| filename | str | |
| page_count | int | |
| status | DocumentStatus | |
| status_detail | str? | reason when not ingested |
| ingested_at | datetime | |

## D. ExtractedInformation
| Field | Type | Note |
|---|---|---|
| field_name | str | canonical name, e.g. `annual_income` |
| value | str or number | normalised value |
| raw_text | str | text as written in the document |
| document_id | str | |
| provenance | Provenance | extracted by LLM and verified, or calculated |
| verified_in_source | bool | value or quote found in page text |
| evidence | DocumentEvidence | |
| confirmed_by_human | bool | |

## E. DocumentEvidence
| Field | Type | Note |
|---|---|---|
| document_id | str | |
| document_type | DocumentType | |
| page_number | int | 1-based |
| quote | str | exact text span |
| section | str? | |
| chunk_id | str? | when retrieved via RAG |

## F. PolicyDocument
| Field | Type | Note |
|---|---|---|
| policy_id | str | |
| title | str | |
| version | str | |
| effective_date | date? | |
| document_id | str | link to Document |
| topics | list[str] | optional tags (dti, ltv, self_employed...) |

## G. PolicyQuery
| Field | Type | Note |
|---|---|---|
| query_id | str | |
| question | str | validated, length-limited |
| scope | enum | policy or applicant |
| applicant_id | str? | required when scope is applicant |
| asked_at | datetime | |

## H. Inconsistency
| Field | Type | Note |
|---|---|---|
| inconsistency_id | str | |
| loan_id | str | |
| field_name | str | |
| kind | enum | numeric, date, text, missing_value |
| values | list[{value, evidence}] | at least two sides, each with evidence |
| difference | str? | calculated by code, Provenance = calculated |
| explanation | str? | AI text, Provenance = ai_generated |
| severity | Severity | |
| review_status | ReviewStatus | |
| reviewer_note | str? | |

## I. UnderwritingSummary
| Field | Type | Note |
|---|---|---|
| loan_id | str | |
| generated_at | datetime | |
| applicant_section | object | name, employment |
| loan_section | object | amount, purpose, term |
| financials | list[ExtractedInformation + calculations] | DTI, LTV marked `calculated` |
| completeness | object | present, missing, unreadable |
| inconsistencies | list[Inconsistency] | |
| policy_observations | list[AIResponse-like item] | each with citation |
| risk_indicators | list[{indicator, basis, severity}] | basis cites rule or evidence |
| human_review_items | list[str] | always present, may be empty only if nothing is flagged |
| narrative | str | `ai_generated` |
| decision | str | fixed value: "pending underwriter" |

## J. AIResponse
| Field | Type | Note |
|---|---|---|
| answer | str | |
| evidence | list[DocumentEvidence] | empty only if `answer` states no evidence was found |
| sources | list[str] | document titles or ids shown to the user |
| confidence | Confidence | qualitative, derived from retrieval relevance and citation checks |
| warnings | list[str] | conflicts, partial evidence, stale policy version |
| requires_human_review | bool | true when evidence is thin, conflicting or missing |
| provenance | Provenance | ai_generated |
| status | enum | ok, no_evidence, partial, failed |

## Invariants
1. Every AI-derived value has at least one DocumentEvidence, or `verified_in_source = false` and a warning.
2. Calculated values never come from an LLM.
3. `UnderwritingSummary.decision` is always "pending underwriter".
4. A missing or conflicting source sets `requires_human_review = true`.
