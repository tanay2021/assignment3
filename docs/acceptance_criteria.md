# POC Acceptance Criteria

Each criterion is pass/fail and has a defined verification (see [test_strategy.md](test_strategy.md)).

| ID | Criterion | Measure | Use case |
|---|---|---|---|
| AC-01 | System ingests the sample loan documents | All documents of LOAN-001 and LOAN-003 reach status `ingested`; pages and chunks stored | UC-01 |
| AC-02 | System extracts the predefined fields | At least 90% of the defined field list (applicant name, loan amount, income, employer, tenure, liabilities, property value, key dates) extracted correctly on LOAN-001 and LOAN-003, each with document and page | UC-01 |
| AC-03 | System identifies missing documents | LOAN-002 reports bank statement as missing and employment verification as unreadable | UC-02 |
| AC-04 | System identifies a cross-document inconsistency | LOAN-001 income mismatch ($120,000 vs $105,000) is reported with both evidences | UC-03 |
| AC-05 | System answers policy questions using RAG | The three policy demo questions return the correct fact; the out-of-corpus question returns "not found" | UC-04 |
| AC-06 | Policy answers include source evidence | 100% of answers cite document, page and quote; no citation points outside retrieved context | UC-04 |
| AC-07 | System generates an underwriting summary | Summary for LOAN-001 contains all sections defined in the UnderwritingSummary contract and ends "pending underwriter" | UC-05 |
| AC-08 | System identifies items requiring human review | Every flagged case (inconsistency, missing document, unverified value, no evidence) appears in `human_review_items` | UC-05 |
| AC-09 | System handles common failures gracefully | Empty, corrupted, unsupported documents, empty retrieval, invalid question and LLM failure each produce a warning and no crash | all |
| AC-10 | All automated tests pass | `pytest` exits 0 | all |
| AC-11 | No API keys or secrets committed | Secrets-scan test passes; `.env` untracked | all |
| AC-12 | Demo runs from documented setup | A fresh clone follows SETUP.md and runs the demo flow without undocumented steps | all |

## Additional guardrail checks (must hold at all times)
- No code path returns an approve/reject decision.
- All DTI/LTV values come from code and are labelled `calculated`.
