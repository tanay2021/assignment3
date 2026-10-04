# Test Strategy

## Principle
**BUILD -> TEST -> VERIFY -> MOVE FORWARD.** Every implementation prompt builds a slice, adds tests for it, runs the full `pytest` suite, verifies the result against its acceptance criteria, and only then moves on. A failing suite blocks the next step.

## Test levels
| # | Level | Scope | Location | LLM/API |
|---|---|---|---|---|
| 1 | Unit | Single function/class (models, calculators, chunker) | `tests/unit/` | none |
| 2 | Integration | Several layers together (ingest -> index -> retrieve) | `tests/integration/` | fake LLM |
| 3 | RAG | Retrieval hit, citation validity, no-evidence behaviour | `tests/integration/rag/` | fake or recorded |
| 4 | Document extraction | PDF loading, page text, unreadable handling, field extraction on synthetic docs | `tests/unit/documents/` + integration | fake LLM for field extraction |
| 5 | Business rules | Completeness, reconciliation, DTI/LTV, thresholds | `tests/unit/loan/`, `tests/unit/policies/` | none |
| 6 | Error handling | Failures degrade gracefully with warnings | both | simulated failures |
| 7 | AI response grounding | Answers cite only retrieved sources; numbers appear in context | `tests/integration/grounding/` | fake LLM returning crafted outputs |
| 8 | Regression | Golden set for the demo package and policy questions | `tests/regression/` | recorded responses |

Default test runs never call the real OpenAI API. An optional marker (`@pytest.mark.live_llm`, off by default) runs a small live smoke test when a key is present.

## Representative scenarios
| Scenario | Expected behaviour | Acceptance |
|---|---|---|
| Valid document | Text and fields extracted with page refs | AC-01, AC-02 |
| Missing document | Listed as missing; package flagged | AC-03 |
| Empty document | Status `empty`, listed as unreadable, rest continues | AC-09 |
| Corrupted document | Status `unreadable`, no crash | AC-09 |
| Conflicting income | Inconsistency with both evidences | AC-04 |
| Missing policy | "No relevant policy found", review flag | AC-05, AC-08 |
| No relevant RAG result | No LLM call, `no_evidence` response | AC-05, AC-09 |
| LLM/API failure | Deterministic results still shown, retryable warning | AC-09 |
| Invalid user question (empty, too long, off-topic) | Validation message or polite refusal | AC-09 |
| Unsupported document type | Status `unsupported`, listed, no crash | AC-09 |
| Hallucinated citation | Citation dropped, warning added | AC-06 |
| Value not found in source | Marked unverified, human review | AC-08 |
| Summary generation | All sections present, decision "pending underwriter" | AC-07 |
| Secrets scan | No keys in tracked files | AC-11 |

## Test data and fakes
- Synthetic package from [demo_data_strategy.md](demo_data_strategy.md); small fixtures built in tests for edge cases (empty and corrupt PDFs generated at test time).
- `FakeLLM` implementing the LLM gateway interface, returning scripted outputs or raising errors.
- Temporary Chroma and SQLite locations via `tmp_path`.

## Traceability: acceptance criteria to tests
| AC | Verified by |
|---|---|
| AC-01 | document ingestion integration test |
| AC-02 | extraction tests on LOAN-001 against expected field table |
| AC-03 | completeness rule tests (LOAN-002) |
| AC-04 | reconciliation tests (LOAN-001 income mismatch) |
| AC-05 | RAG tests with policy golden questions |
| AC-06 | grounding tests (citation present and valid) |
| AC-07 | summary service test |
| AC-08 | tests asserting `requires_human_review` for each flagged case |
| AC-09 | error-handling tests |
| AC-10 | full `pytest` run in CI/local |
| AC-11 | secrets-scan test (tracked files contain no key patterns) |
| AC-12 | end-to-end run following SETUP.md (Prompt 9) |

## Definition of done for any prompt
Tests written for new behaviour, full suite green, no new warnings caused by our code, docs updated if the architecture changed.
