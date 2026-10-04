# AI Capability Mapping

Principle: **AI for understanding, ML for prediction, RAG for knowledge, Rules for deterministic decisions, APIs/automation for execution, Humans for critical decisions.**

| # | Capability | Technology pattern | Reason |
|---|---|---|---|
| 1 | PDF text extraction per page | Document processing (PyMuPDF) | Deterministic, keeps page numbers |
| 2 | Unreadable/empty document detection | Traditional code | Simple checks (no text, open error) |
| 3 | Document type classification | Rules first (filename/keywords), LLM fallback | Cheap and predictable; LLM only for ambiguous cases |
| 4 | Field extraction (name, income, employer, etc.) | LLM with structured output + validation rules | Layouts vary, schema is fixed; output validated by code |
| 5 | Locating the source quote/page for a value | Code (string search over page text) | Verifies the LLM did not invent the value |
| 6 | Document completeness | Rules/Code | Expected list is a deterministic checklist |
| 7 | Numeric inconsistency detection | Rules/Code | Exact comparison with tolerance |
| 8 | Semantic inconsistency (e.g. "self-employed" vs "salaried", name variants) | LLM + Rules | Meaning comparison, then deterministic confirmation of evidence |
| 9 | DTI, LTV, income totals | Rules/Code | Deterministic calculation, never delegated to the LLM |
| 10 | Policy lookup | RAG | Knowledge retrieval with citations |
| 11 | Applicant fact Q&A | RAG (filtered by applicant) | Grounded answers from loan documents |
| 12 | Policy compliance observations (e.g. "DTI 46% exceeds 43% limit") | Rules for the comparison, RAG for the policy value | Threshold taken from retrieved policy, comparison done in code |
| 13 | Narrative summary wording | LLM | Language generation over verified inputs |
| 14 | Risk indicators | Rules + LLM narrative | Indicators come from rules/flags; LLM only words them |
| 15 | Multi-step review orchestration | Plain Python pipeline; LangGraph only for the summary workflow | State and human checkpoints justify a graph; elsewhere it is overhead |
| 16 | OCR for scanned documents | Deferred / fallback | Not needed for synthetic text PDFs |
| 17 | Credit/default prediction | **Not used** | Out of scope; no ML model in POC |
| 18 | Final approve/reject decision | **Human** | Critical business and regulatory decision |
| 19 | Resolving inconsistencies | **Human** | Requires judgment and applicant contact |

## Where Agentic AI is (and is not) used
- **Not used** for extraction, completeness, reconciliation, policy Q&A. These are fixed, testable pipelines.
- **Considered only** for UC-05 (summary assembly), where several tools (calculators, retriever, flag collector) are combined and a human-review gate is needed. Even there the graph is a fixed workflow with defined nodes, not free-running tool selection.

## Guardrails common to all LLM usage
- Structured output validated against schemas.
- Every extracted value verified against source text.
- Temperature low; prompts instruct "answer only from context".
- Output labelled `ai_generated` vs `calculated` vs `extracted`.
- Failures degrade to the deterministic result plus a visible warning.
