# Data Flow

Legend: **[D]** deterministic logic, **[AI]** LLM reasoning, **[R]** retrieval, **[H]** human review.

## 1. Ingestion (document intelligence + indexing)
```
Loan documents (PDF)
  -> Document loader                 [D]  open file, detect unreadable/empty/unsupported
  -> Text extraction per page        [D]  PyMuPDF, keep page_number
  -> Document type classification    [D] rules, [AI] fallback for ambiguous files
  -> Chunking                        [D]  page/section aware
  -> Metadata attach                 [D]  document_id, type, applicant_id, page, source, section, timestamp
  -> Embeddings                      [D]  sentence-transformers (local)
  -> Vector store (ChromaDB)         [D]  collections: loan_documents, policies
  -> Document record + status        [D]  SQLite
```
Policy documents follow the same path into the `policies` collection.

## 2. Field extraction (UC-01)
```
Page text -> LLM structured extraction [AI] -> schema validation [D]
  -> source quote lookup in page text [D]  (value not found in text => flagged, not trusted)
  -> ExtractedInformation + DocumentEvidence stored [D]
  -> Underwriter confirms/corrects [H]
```

## 3. Document completeness (UC-02)
```
Loan package + expected document list (config) [D]
  -> compare present vs expected [D]
  -> unreadable documents from ingestion status [D]
  -> Completeness report: present / missing / unreadable [D]
  -> Missing or unreadable items shown for follow-up [H]
```
No AI is used.

## 4. Information reconciliation (UC-03)
```
Extracted fields grouped by canonical field name [D]
  -> numeric/date comparison with tolerance [D]
  -> semantic comparison for text fields (names, employment type) [AI]
  -> evidence attached for each side (document, page, quote) [D]
  -> Inconsistency list with severity [D]
  -> Underwriter sets status: resolved / follow-up / accepted [H]
```

## 5. Policy and applicant Q&A (UC-04, UJ-02)
```
Question -> input validation [D] -> choose collection (policies | applicant docs) [D]
  -> embed question [D] -> retrieve top-k with metadata filter [R]
  -> relevance threshold check [D]  (nothing relevant => "not found", no LLM guess)
  -> context builder with numbered sources [D]
  -> LLM grounded answer, "use only the context" [AI]
  -> citation check: cited source ids exist in context [D]
  -> AIResponse (answer, evidence, warnings, requires_human_review) [D]
  -> Underwriter verifies against cited page [H]
```

## 6. Underwriting summary (UC-05)
```
Extracted fields + completeness + inconsistencies          [D]
  -> DTI, LTV, income totals                               [D]
  -> retrieve policy thresholds (DTI max, LTV max, docs)   [R]
  -> compare calculated values with thresholds             [D]
  -> risk indicators from rules                            [D]
  -> narrative wording over verified inputs                [AI]
  -> assemble summary, tag each section ai_generated / calculated / extracted [D]
  -> list items requiring human review                     [D]
  -> Underwriter reviews, edits, decides outside system    [H]
```
The summary always ends with "Decision: pending underwriter".

## 7. Where each kind of logic lives
| Kind | Steps |
|---|---|
| Deterministic | loading, page extraction, chunking, completeness, numeric comparison, calculations, threshold comparison, citation checks |
| AI reasoning | field extraction, semantic comparison, grounded answers, narrative wording |
| Retrieval | policy Q&A, applicant Q&A, policy thresholds for the summary |
| Human review | field confirmation, inconsistency resolution, answer verification, final decision |
