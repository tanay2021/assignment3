# Demo Data Strategy

All data is **synthetic** and marked as such in each document. Documents are created in later prompts (Prompt 3 onward); this file only defines them. Policy thresholds below are invented for the demo.

## Loan packages
| Package | Purpose | Documents present | Deliberate feature |
|---|---|---|---|
| **LOAN-001** | Main demo, inconsistency | Application, Salary slip, Employment verification, Bank statement, Property document | Application states annual income $120,000; salary slip implies $105,000 |
| **LOAN-002** | Completeness | Application, Salary slip, Employment verification, Property document | Bank statement missing; employment verification is an empty/unreadable PDF |
| **LOAN-003** | Happy path | All five documents | Consistent values; policy checks pass (baseline for regression) |
| **LOAN-004** (optional) | Self-employed policy question | Application, tax return summary | Exercises "documents required for self-employed" policy |

## LOAN-001 documents
| # | Document | Key content (synthetic) |
|---|---|---|
| 1 | Loan Application | Applicant name, requested amount, purpose, term, stated annual income $120,000, employer, existing monthly liabilities, property address |
| 2 | Salary Slip / Income Document | Employer, monthly gross, annual equivalent $105,000, pay period |
| 3 | Employment Verification | Employer letter: title, start date (tenure), employment type, confirms salary band |
| 4 | Bank Statement | 3 months of transactions, monthly salary credits, average balance, recurring obligations |
| 5 | Property Document | Address, appraised value, ownership/title summary |
| 6 | Loan Policy (shared) | See below |

Liabilities and property value are chosen so that DTI and LTV calculations produce meaningful values, with the stated-versus-verified income changing whether DTI is under or over the policy limit. This demonstrates why the inconsistency matters.

## Policy corpus (`data/sample_policies`)
| Document | Topics | Example content |
|---|---|---|
| Underwriting Policy v2025.1 | DTI, LTV, credit score, income documentation, employment tenure | Max DTI 43%; max LTV 80%; minimum 2 years employment history |
| Documentation Requirements | Required documents by applicant type | Salaried: application, salary slip, employment verification, bank statements, property document. Self-employed: adds tax returns and business statements |
| Exceptions and Escalation | When to escalate to senior underwriter | DTI above limit needs senior review |

Enough varied content (about 8-12 pages total) for RAG to retrieve across documents, including one question with no answer in the corpus (for the "no relevant policy" scenario).

## Demo questions
| Question | Expected source |
|---|---|
| What is the maximum acceptable debt-to-income ratio? | Underwriting Policy, DTI section |
| What documents are required for self-employed applicants? | Documentation Requirements |
| What income documentation is required? | Documentation Requirements |
| What is the applicant's employer and tenure? | LOAN-001 employment verification |
| What is the policy on cryptocurrency income? | None (expect "not found") |

## Edge fixtures (generated in tests, not shipped)
Empty PDF, corrupted PDF bytes, unsupported file type (.docx), duplicate upload.

## Rules for synthetic data
Invented names and addresses only; no real employers, account numbers or ids; amounts rounded and plausible; a visible "SYNTHETIC SAMPLE" footer on each document.
