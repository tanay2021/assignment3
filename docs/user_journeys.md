# User Journeys

All journeys are for the **Underwriter** persona. Use cases: UC-01 to UC-05 (see [poc_scope.md](poc_scope.md)).

## UJ-01: Underwriter reviews a new loan package
| Item | Detail |
|---|---|
| User | Underwriter |
| Starting point | A loan package (e.g. LOAN-001) is available in the app |
| User action | Selects the loan package and clicks "Review package" |
| System action | Loads documents, extracts text per page, runs field extraction, runs completeness check, runs reconciliation |
| AI capability | Document intelligence (extraction), LLM-assisted field extraction, LLM + rules reconciliation |
| Expected result | Dashboard with extracted fields (each with source and page), a document checklist, and a list of inconsistencies |
| Human decision | Underwriter confirms or corrects extracted fields and decides which flags to pursue |
| Failure / exception | A document is empty, corrupted or an unsupported type: it is marked "unreadable" and listed for human attention; processing continues with the rest. LLM/API failure: the deterministic parts (completeness) still display and the failed step shows a retryable error |

## UJ-02: Underwriter asks a question about applicant information
| Item | Detail |
|---|---|
| User | Underwriter |
| Starting point | A reviewed package is open |
| User action | Types "What is the applicant's employer and tenure?" |
| System action | Retrieves relevant chunks from this applicant's documents only (filtered by applicant_id), builds context, generates a grounded answer |
| AI capability | RAG + LLM |
| Expected result | Short answer with citations (document, page). If evidence is missing, the answer says "not found in the loan documents" |
| Human decision | Underwriter verifies against the cited page |
| Failure / exception | No relevant chunk: system declines to answer instead of guessing. Question out of domain: polite refusal with guidance. LLM failure: error message and the retrieved passages are still shown |

## UJ-03: Underwriter asks a policy question
| Item | Detail |
|---|---|
| User | Underwriter |
| Starting point | Policy documents are indexed |
| User action | Asks "What is the maximum acceptable debt-to-income ratio?" |
| System action | Retrieves from the policy collection, builds context, generates a grounded answer with citations |
| AI capability | RAG + LLM |
| Expected result | Answer such as "43% (Policy, section 4.2, page 7)" plus the quoted passage |
| Human decision | Underwriter decides how the policy applies |
| Failure / exception | Policy topic not covered: "No relevant policy found", flagged for human review. Conflicting passages: both are shown and flagged |

## UJ-04: Underwriter investigates an inconsistency
| Item | Detail |
|---|---|
| User | Underwriter |
| Starting point | Reconciliation lists "Annual income: $120,000 (application) vs $105,000 (salary slip)" |
| User action | Opens the inconsistency |
| System action | Shows both values side by side with document name, page and quoted text; shows the difference computed by code; offers an AI explanation of possible causes (labelled as AI-generated) |
| AI capability | Rules (detection of numeric mismatch), LLM (semantic comparison, plain-language explanation) |
| Expected result | Evidence panel and a status the underwriter can set: Resolved / Needs follow-up / Accepted |
| Human decision | Underwriter resolves or requests clarification from the applicant |
| Failure / exception | Source quote cannot be located: inconsistency is shown with a warning that evidence is partial |

## UJ-05: Underwriter generates an underwriting summary
| Item | Detail |
|---|---|
| User | Underwriter |
| Starting point | Package reviewed, inconsistencies triaged |
| User action | Clicks "Generate summary" |
| System action | Assembles applicant and loan data, extracted financials, completeness, inconsistencies, DTI/LTV calculations (code), relevant policy observations (RAG), risk indicators and a list of items requiring human review |
| AI capability | LLM for narrative and policy observations; rules/code for calculations; optional LangGraph workflow for the multi-step assembly |
| Expected result | Structured summary where every claim has a source reference and AI text is distinguished from calculated values. It ends with "Decision: pending underwriter" |
| Human decision | Underwriter reviews, edits and makes the final decision outside the system |
| Failure / exception | Missing inputs (e.g. no bank statement): the section is marked "incomplete" and added to the review list. LLM failure: summary is produced with deterministic sections only and a notice |

## Coverage
| Journey | Use cases covered |
|---|---|
| UJ-01 | UC-01, UC-02, UC-03 |
| UJ-02 | UC-01 (retrieval of applicant facts) |
| UJ-03 | UC-04 |
| UJ-04 | UC-03 |
| UJ-05 | UC-05 (uses UC-01 to UC-04 outputs) |
