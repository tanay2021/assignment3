# Security and Responsible AI Baseline

## Security controls
| # | Control | How it is enforced |
|---|---|---|
| S1 | No API keys in git | `.env` in `.gitignore`; only `.env.example` (empty values) is tracked; check before each commit |
| S2 | No secrets in source | Secrets read only through `app/config.py` |
| S3 | No secrets in logs | Settings are never logged whole; the LLM gateway logs model, latency and token counts, never headers or keys |
| S4 | No real PII | All loan data is synthetic; documents carry a "SYNTHETIC" marker; never paste real customer data into prompts or tests |
| S5 | Minimal data sent to the LLM | Only the needed page text or retrieved chunks; no whole-package dumps |
| S6 | Local data stores git-ignored | SQLite files and `chroma/` are ignored |
| S7 | Input validation | Question length and type limits; uploads restricted to supported types and size |
| S8 | Dependency discipline | Pinned versions; changes need justification |

## Responsible AI controls
| # | Control |
|---|---|
| R1 | **No autonomous decisions.** No code path outputs approve/reject; summary ends with "Decision: pending underwriter" |
| R2 | Every statement is labelled `extracted`, `calculated` or `ai_generated` |
| R3 | Calculations (DTI, LTV, sums) are done in code, never by the LLM |
| R4 | Evidence preserved: document, page, quote for every value and citation |
| R5 | Unverified values (not found in source text) are flagged, not hidden |
| R6 | Uncertain, missing or conflicting information sets `requires_human_review` |
| R7 | The assistant says "not found" instead of guessing |
| R8 | Humans confirm extracted fields and resolve inconsistencies |
| R9 | The UI shows a standing notice: "AI-assisted. The underwriter makes the final decision." |
| R10 | Applicant questions are scoped to the applicant, preventing cross-case leakage |

## Known POC limitations
- Synthetic, clean, text-based PDFs only; real-world scans, handwriting and odd layouts are untested.
- LLM output can be wrong or inconsistent between runs; evidence checks reduce but do not remove this.
- No fairness or bias evaluation; no decision model exists, so none is claimed.
- No authentication, audit trail beyond logs, or encryption at rest.
- Data goes to a third-party API (OpenAI); acceptable only for synthetic data.
- Policy content is invented for the demo and is not real lending policy.

## Out of scope for the POC but required before production
Regulatory review, model risk management, access control, audit logging, data retention, PII redaction, bias testing, vendor risk assessment.
