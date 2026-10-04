# Implementation Roadmap

Each prompt follows BUILD -> TEST -> VERIFY -> MOVE FORWARD. No prompt starts until the previous suite is green. The recommended sequence is kept, with two small adjustments noted in ADR-007.

| Prompt | Title | Builds | Depends on | Acceptance criteria advanced |
|---|---|---|---|---|
| 2 | Application Foundation + Domain Models | `src/domain` models from [data_contracts.md](data_contracts.md); `src/data` SQLite repositories; result/error types; service skeletons; `trace_step` logging helper; FakeLLM interface | 0, 1 | foundation for all; AC-10 |
| 3 | Document Intelligence + Synthetic Data | Synthetic documents for LOAN-001..003 and policies; PDF loader, page extraction, unreadable handling, type classification, completeness check | 2 | AC-01, AC-03, AC-09 |
| 4 | Knowledge Base + RAG | Chunking, metadata, embeddings, Chroma wrapper, retrieval, context builder, citations, grounded answers via LLM gateway | 2, 3 | AC-05, AC-06 |
| 5 | Loan Information Intelligence + Reconciliation | LLM field extraction with source verification, canonical fields, reconciliation, DTI/LTV calculators | 3, 4 | AC-02, AC-04 |
| 6 | Policy Intelligence + Controlled Reasoning | Threshold extraction from retrieved policy, compliance comparison, risk indicators, human-review flags | 4, 5 | AC-05, AC-08 |
| 7 | Underwriting Summary + Streamlit UX | Summary service (LangGraph workflow if justified), Streamlit screens for UJ-01..05, human review actions | 5, 6 | AC-07, AC-08 |
| 8 | Evaluation + Observability + Hardening | Golden sets, grounding checks, structured tracing hook, retries/timeouts, secrets-scan test | 7 | AC-06, AC-09, AC-11 |
| 9 | End-to-End Testing + Demo Preparation | E2E scenario tests, demo script, README/SETUP verification on a clean clone | 8 | AC-10, AC-12 |

## Dependency logic
```
domain/data (2) -> documents + synthetic data (3) -> RAG (4) -> extraction + reconciliation (5)
   -> policy reasoning (6) -> summary + UI (7) -> hardening (8) -> E2E + demo (9)
```

## Notes
- The synthetic documents are created in Prompt 3 (not 9) because every later prompt needs them to test against.
- The LLM gateway interface and FakeLLM are defined in Prompt 2 so Prompts 3-7 can be tested without network access.
- Prompt 1 decisions can only change through an ADR (see [architecture_decisions.md](architecture_decisions.md)).

## Per-prompt exit checklist
1. New behaviour has tests; full `pytest` green.
2. No new dependency without justification.
3. No secrets or real PII added.
4. Docs updated if the design changed.
5. Acceptance criteria status recorded.
