# Business Requirements

## A. Business problem
Loan underwriters spend most of their time finding, reading and cross-checking information scattered across application forms, income proofs, employment letters, bank statements, property papers and policy manuals. The work is slow, repetitive and error-prone. Inconsistencies (for example, stated income that does not match the salary slip) are found late or missed, and policy answers depend on who remembers which clause.

## B. Current / manual process
```
Loan Application -> Document Collection -> Document Review -> Data Extraction
   -> Data Validation -> Policy Checking -> Underwriting Analysis -> Human Decision
```
| Stage | How it is done today |
|---|---|
| Document collection | Associate checks a paper/email checklist by hand |
| Document review | Underwriter opens each PDF and reads it |
| Data extraction | Values are re-keyed into a worksheet |
| Data validation | Underwriter compares figures across documents by eye |
| Policy checking | Underwriter searches a policy PDF or asks a colleague |
| Analysis | Underwriter writes a summary note from memory and worksheet |
| Decision | Underwriter decides (this stays human) |

## C. Key pain points
1. Time lost locating facts across multiple documents.
2. Manual re-keying introduces transcription errors.
3. Cross-document inconsistencies are easy to miss.
4. Missing documents are discovered late, delaying the file.
5. Policy lookup is slow and inconsistent between underwriters.
6. Summary notes lack consistent structure and source references, so reviewers cannot trace claims.

## D. Users / personas
| Persona | Role in POC | Priority |
|---|---|---|
| **Underwriter** | Reviews packages, asks questions, decides | **Primary, the POC is built for this persona** |
| Loan Processing Associate | Collects documents, checks completeness | Secondary (benefits from UC-02) |
| Loan Operations Analyst | Monitors file quality and turnaround | Secondary (not designed for) |
| Credit/Risk Analyst | Defines policy, audits outcomes | Secondary (not designed for) |

## E. Business objectives
- BO-1 Reduce time to understand a loan package.
- BO-2 Surface cross-document inconsistencies early, with evidence.
- BO-3 Give consistent, cited answers to policy questions.
- BO-4 Produce a structured, evidence-backed underwriting summary.
- BO-5 Keep the underwriter in control: AI assists, never decides.

## F. Expected AI-assisted improvements
| Pain point | AI-assisted improvement |
|---|---|
| Finding facts | Extraction with page-level source references |
| Re-keying | Pre-populated structured fields for the underwriter to confirm |
| Missed inconsistencies | Automatic cross-document comparison with side-by-side evidence |
| Late missing documents | Immediate completeness check against the expected list |
| Slow policy lookup | Natural-language policy Q&A with citations |
| Inconsistent notes | Generated summary in a fixed structure, with items flagged for human review |

## G. POC success definition
The POC succeeds if, on a synthetic loan package, a reviewer can watch the system (1) extract fields with sources, (2) report a missing document, (3) flag a cross-document inconsistency with evidence, (4) answer policy questions with citations, and (5) produce a summary that explicitly lists items needing human review, all without making a loan decision. Measurable criteria are in [acceptance_criteria.md](acceptance_criteria.md).
