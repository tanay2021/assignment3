# RAG Design

Goal: answer "What does the policy say?" and "Where did this information come from?" with traceable sources. Implemented in Prompt 4; this is the blueprint.

## 1. Two collections
| Collection | Content | Filter |
|---|---|---|
| `loan_documents` | Pages of a loan package | `applicant_id`, `document_type` |
| `policies` | Underwriting policy documents | `policy_id`, `version` |

Separate collections prevent policy text from being cited as applicant evidence and vice versa.

## 2. Pipeline
| Step | Design |
|---|---|
| 1. Ingestion | Load PDF files from `data/sample_documents` and `data/sample_policies`; record a Document row in SQLite |
| 2. Text extraction | PyMuPDF per page; store `page_number`; empty/corrupt pages mark the document status, never silently skipped |
| 3. Chunking | Split by headings/sections where detectable, else by paragraphs; target ~500 tokens with ~50 overlap; a chunk never spans two pages (so page citation is exact) |
| 4. Metadata | See table below |
| 5. Embeddings | sentence-transformers, one local model, fixed in config; same model for indexing and queries |
| 6. Vector storage | ChromaDB persistent client under a git-ignored folder (`chroma/`); deterministic chunk ids (`document_id:page:index`) so re-ingestion is idempotent |
| 7. Retrieval | Top-k (default 5) with metadata filter; relevance threshold; if nothing passes, return `no_evidence` without calling the LLM |
| 8. Context construction | Numbered sources `[1]..[k]` with title, page and section; capped to a token budget; policy version included |
| 9. Response generation | LLM instructed: answer only from context, cite source numbers, say "not found" otherwise; low temperature; JSON with `answer`, `citations` |
| 10. Source citation | Citation numbers are mapped back to DocumentEvidence; any citation not in the context is dropped and a warning added |

## 3. Metadata schema
| Key | Example | Purpose |
|---|---|---|
| document_id | DOC-001-APP | trace to Document |
| document_type | application | filtering, display |
| applicant_id | APP-001 (absent for policies) | per-applicant isolation |
| page_number | 2 | citation |
| source | `application_form.pdf` | citation text |
| section | "Employment details" | citation, better context |
| chunk_index | 0 | stable id |
| ingestion_timestamp | ISO-8601 | audit, staleness |
| policy_id / policy_version | POL-001 / 2025.1 | policy answers cite the version |

## 4. Answering "Where did this come from?"
Each answer shows: document name, page number, section and the exact quote. For extracted fields (not RAG), the quote is located by string search in page text; if it cannot be found, the field is marked unverified.

## 5. Grounding rules
1. No context, no answer: empty retrieval returns "No relevant information found" and `requires_human_review = true`.
2. Conflicting passages (e.g. two policy versions) are both shown with a warning.
3. Numbers in an answer must appear in a cited chunk; a post-check flags numbers not found in context.
4. Applicant questions are filtered by `applicant_id` to avoid cross-applicant leakage.
5. The LLM never computes ratios; the service layer provides calculated values.

## 6. Evaluation (feeds Prompt 8)
Small golden set of question, expected source page and expected answer fragment. Metrics: retrieval hit (right page in top-k), citation validity, answer contains expected fact, refusal on out-of-scope questions.

## 7. Deliberately excluded
Hybrid search, re-rankers, query rewriting, multi-hop agents. Add only if the golden set shows a gap, and record an ADR.
