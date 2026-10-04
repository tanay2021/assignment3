# Architecture

## 1. Stack (unchanged from Prompt 0)
| Concern | Choice |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3.11 |
| Orchestration | LangChain; LangGraph only where state and human checkpoints help (summary workflow) |
| LLM | OpenAI API |
| Document processing | PyMuPDF (OCR deferred) |
| Embeddings | sentence-transformers |
| Vector DB | ChromaDB |
| Relational data | SQLite (standard library `sqlite3`) |
| Config / logging / tests | python-dotenv / `logging` / pytest |
| Observability | Structured logging now; Langfuse-ready through a thin tracing hook |

No new dependencies are introduced by this blueprint.

## 2. Layered view
```
+--------------------------------------------------------------+
| 1. Presentation (Streamlit)         app/ui/                  |  display only, no business logic
+------------------------------+-------------------------------+
                               | calls
+------------------------------v-------------------------------+
| 2. Application / Service layer      src/services/            |  use-case orchestration (UC-01..05)
+-----+------------+------------+------------+-----------------+
      |            |            |            |
+-----v----+ +-----v----+ +-----v----+ +-----v-----+
| 3. Doc   | | 4. RAG / | | 5. Loan  | | 6. Policy |
| Intellig.| | Knowledge| | Intellig.| | Intellig. |
| src/     | | src/rag/ | | src/loan/| | src/      |
| documents| |          | |          | | policies/ |
+-----+----+ +-----+----+ +-----+----+ +-----+-----+
      |            |            |            |
+-----v------------v------------v------------v-----------------+
| 7. LLM service        src/services/llm/   (single OpenAI gateway)
| 8. Data access        src/data/           (SQLite repos, Chroma wrapper)
| 9. Domain models      src/domain/         (shared Python models/contracts)
+--------------------------------------------------------------+
| 10. Cross-cutting: Configuration app/config.py | Logging app/logging_config.py
+--------------------------------------------------------------+
```

## 3. Component responsibilities and mapping to the repo
| # | Component | Location | Responsibility | Must not |
|---|---|---|---|---|
| 1 | Presentation | `app/ui/` (new, Prompt 7) | Render screens, capture input, call services | Contain business rules, call OpenAI/Chroma directly |
| 2 | Application services | `src/services/` | One service per use case; coordinates layers 3-8; owns error handling and human-review flags | Parse PDFs or build prompts itself |
| 3 | Document Intelligence | `src/documents/` | Load PDFs, extract page text, classify type, detect unreadable files, extract fields, locate source quotes | Know about policies or the UI |
| 4 | RAG / Knowledge | `src/rag/` | Chunking, metadata, embeddings, indexing, retrieval, context building, citations | Decide business outcomes |
| 5 | Loan Intelligence | `src/loan/` | Completeness rules, reconciliation, DTI/LTV and other calculations, risk indicator rules | Call the LLM for calculations |
| 6 | Policy Intelligence | `src/policies/` | Policy Q&A, extraction of thresholds from retrieved policy, compliance comparison | Make final decisions |
| 7 | LLM service | `src/services/llm/` (new) | Single gateway to OpenAI: prompts, structured output, retries, timeouts, error mapping | Be called from the UI or by layers other than 2-6 |
| 8 | Data access | `src/data/` (new) | SQLite repositories (loan packages, documents, extracted fields, inconsistencies, review status), ChromaDB wrapper | Contain business logic |
| 9 | Domain models | `src/domain/` (new) | Python models for the contracts in [data_contracts.md](data_contracts.md) | Import from other layers |
| 10 | Config and logging | `app/config.py`, `app/logging_config.py` (exist) | Settings, validation, log setup | Print secrets |

New folders (`app/ui`, `src/domain`, `src/data`, `src/services/llm`) are the only structural additions; see ADR-004 in [architecture_decisions.md](architecture_decisions.md).

### Dependency rule
Dependencies point downward only: UI -> services -> {documents, rag, loan, policies} -> {llm, data} -> domain. `domain` imports nothing from the project. Layers 3-6 never import each other; the service layer composes them. This keeps modules loosely coupled and individually testable with fakes.

## 4. Orchestration approach
- UC-01, UC-02, UC-03, UC-04: plain Python service methods (linear, easy to test).
- UC-05: a LangGraph workflow with nodes `gather_inputs -> calculate -> policy_observations -> draft_summary -> flag_for_review`, state held in a typed dict, ending at a human-review gate. If LangGraph proves unnecessary during Prompt 7, fall back to a plain function (record in an ADR).

## 5. Observability
Structured logs (job id, step, duration, outcome, counts) through the existing logger. A small `trace_step` helper in services wraps each step so Langfuse can be attached later without touching business code. Prompts and responses are logged only at DEBUG and never contain secrets; synthetic data only.

## 6. Error-handling model
Every service call returns a result object with `status` (ok / partial / failed), `warnings`, and `requires_human_review`. Layers raise typed domain errors (`DocumentUnreadableError`, `LLMUnavailableError`, `NoEvidenceError`); the service layer converts them to results. The UI shows warnings; it never sees raw stack traces.

## 7. Validation of this architecture
| Check | Result |
|---|---|
| Requirements consistent with journeys | BO-1..5 map to UJ-01..05 (see [user_journeys.md](user_journeys.md) coverage table) |
| Journeys supported by architecture | Each journey step maps to a service in layer 2 and a component in layers 3-8 (table below) |
| Components map to repo | Section 3; four new folders flagged |
| Data flow matches architecture | [data_flow.md](data_flow.md) names the same components |
| AI choices justified | [ai_capability_mapping.md](ai_capability_mapping.md) gives a reason per capability; LLM never does arithmetic or decisions |
| RAG supports traceability | Metadata schema carries document_id, page_number, applicant_id etc. ([rag_design.md](rag_design.md)) |
| Security reflected | Single LLM gateway, config-only secrets, synthetic data, evidence-labelling ([security_responsible_ai.md](security_responsible_ai.md)) |
| Tests cover acceptance criteria | Traceability matrix in [test_strategy.md](test_strategy.md) |
| Roadmap follows dependencies | domain -> documents -> rag -> loan -> policy -> summary/UI -> hardening ([implementation_roadmap.md](implementation_roadmap.md)) |
| No unnecessary technology | No additions to `requirements.txt`; SQLite via stdlib |

### Journey to component trace
| Journey | Service (layer 2) | Components used |
|---|---|---|
| UJ-01 | `ReviewPackageService` | documents, loan (completeness, reconciliation), llm, data |
| UJ-02 | `ApplicantQAService` | rag (applicant collection), llm |
| UJ-03 | `PolicyQAService` | rag (policy collection), policies, llm |
| UJ-04 | `InconsistencyService` | loan, documents (quote lookup), llm, data (status) |
| UJ-05 | `SummaryService` | loan (calculations), policies, llm, data; LangGraph workflow |
