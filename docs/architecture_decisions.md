# Architecture Decisions

Format: context, decision, rationale, consequences. Status is Accepted unless stated. Changing an accepted decision requires a new ADR.

## ADR-001: Human makes every final loan decision
- **Context:** Lending is regulated and high-impact.
- **Decision:** The system assists and flags; it never approves or rejects. The summary ends with "Decision: pending underwriter".
- **Rationale:** Accountability, regulatory expectations, POC credibility.
- **Consequences:** No decision model; risk indicators are descriptive.

## ADR-002: Rules for calculations, LLM for understanding
- **Decision:** DTI, LTV, sums and threshold comparisons run in code; the LLM extracts, compares meaning, answers from context and words narratives.
- **Rationale:** LLMs are unreliable at arithmetic; deterministic results are testable.
- **Consequences:** Policy thresholds come from retrieved policy text, parsed into values and compared in code.

## ADR-003: RAG with mandatory citations and "no evidence, no answer"
- **Decision:** Answers are generated only from retrieved chunks, carry document/page/quote citations, and empty retrieval skips the LLM.
- **Rationale:** Traceability and reduced hallucination.
- **Consequences:** Retrieval quality is critical; a golden set is needed (Prompt 8).

## ADR-004: Layered modules with four new folders
- **Decision:** Add `app/ui/`, `src/domain/`, `src/data/`, `src/services/llm/` to the Prompt 0 layout; dependencies point downward only; the UI contains no business logic.
- **Rationale:** Maps the 10 required layers onto the existing structure with minimal additions.
- **Consequences:** Layers are testable with fakes.

## ADR-005: Single LLM gateway
- **Decision:** All OpenAI calls go through `src/services/llm/`, which handles prompts, structured output, retries, timeouts, logging without secrets, and error mapping.
- **Rationale:** One place for security, cost control and future Langfuse tracing; enables a FakeLLM.
- **Consequences:** Other modules depend on an interface, not the SDK.

## ADR-006: Two Chroma collections (loan documents, policies)
- **Decision:** Separate collections with metadata filters (applicant_id, document_type, policy version).
- **Rationale:** Prevents policy/evidence confusion and cross-applicant leakage.

## ADR-007: Roadmap adjustments
- **Decision:** Keep the recommended Prompt 2-9 order. Synthetic data creation moves into Prompt 3, and FakeLLM/gateway interface into Prompt 2.
- **Rationale:** Later prompts need test data and offline LLM fakes.

## ADR-008: LangGraph only for the summary workflow
- **Decision:** UC-01 to UC-04 use plain Python service methods; UC-05 may use LangGraph for staged state and a human-review gate. If it adds no value in Prompt 7, use plain code and record an ADR.
- **Rationale:** Avoid framework overhead where a function suffices.

## ADR-009: SQLite through the standard library; no ORM
- **Decision:** Use `sqlite3` with simple repository classes; store loan packages, document status, extracted fields, inconsistencies and review status.
- **Rationale:** No new dependency; schema stays small.
- **Consequences:** Migrations are manual scripts for the POC.

## ADR-010: OCR deferred
- **Decision:** No OCR; synthetic PDFs are text-based. Image-only pages are marked `unreadable` and flagged.
- **Rationale:** Not needed for the demo; avoids heavy dependencies.

## ADR-011: Tests never need the network
- **Decision:** Default tests use FakeLLM and temporary stores; live LLM tests are opt-in via a marker.
- **Rationale:** Deterministic, free, safe in CI.

## ADR-012: Qualitative confidence
- **Decision:** Responses carry `high/medium/low` confidence based on retrieval relevance and citation checks, not a numeric probability.
- **Rationale:** LLM self-reported probabilities are not calibrated; qualitative labels set honest expectations.

## Open questions
1. Which sentence-transformers model balances size and quality on the target laptop?
2. Which OpenAI model is used for extraction versus narrative (cost/quality)?
3. Does the demo need a PDF upload screen, or only pre-loaded packages?
4. Is LangGraph worth its weight for the summary workflow? (decided in Prompt 7)
