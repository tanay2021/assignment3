# POC Scope

## In scope
| ID | Use case | Summary |
|---|---|---|
| UC-01 | Loan document understanding | Extract underwriting fields from sample documents, keeping document and page references |
| UC-02 | Document completeness check | Report present, missing and potentially unreadable documents |
| UC-03 | Information reconciliation | Compare values across documents and present evidence for each mismatch |
| UC-04 | Policy knowledge assistant | Answer policy questions grounded in policy documents, with citations |
| UC-05 | Underwriting summary | Generate a structured, evidence-backed summary with human-review items |

Primary persona: **Underwriter**. Input: synthetic text-based PDFs. UI: simple local Streamlit app (built in Prompt 7).

## Out of scope
- Autonomous approval, rejection or pricing of loans.
- Credit scoring or any predictive ML model.
- Real customer data or PII.
- OCR of scanned images (future/fallback; only if sample documents require it).
- Integrations with a loan origination system, credit bureaus or core banking.
- Authentication, multi-tenancy, role-based access.
- Production deployment, scaling, high availability.
- Multi-language documents.
- Fine-tuning models.

## Assumptions
- Sample documents are synthetic, English, text-based PDFs.
- One loan package is reviewed at a time.
- The OpenAI API is available for development and demo.
- The policy corpus is small (a handful of synthetic documents).

## POC limitations
Accuracy is not production-grade. Extraction may miss fields in unusual layouts. LLM output can be wrong, which is why every AI statement carries evidence and a human-review flag. See [security_responsible_ai.md](security_responsible_ai.md).

## Non-negotiable constraint
The system never emits a final approve/reject decision. It may report "risk indicators" and "items requiring human review" only.
