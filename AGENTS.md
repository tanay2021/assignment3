# AGENTS.md: Rules for all coding work on this project

Project: Intelligent Loan Underwriting Assistant (BFSI POC). Read `docs/architecture.md`, `docs/architecture_decisions.md` and `docs/implementation_roadmap.md` before changing code.

## Architecture
- Follow the approved architecture. Do not silently change it. If a change is needed, write a new ADR in `docs/architecture_decisions.md` and update affected docs.
- Layers: UI (`app/ui`) -> services (`src/services`) -> documents / rag / loan / policies -> llm gateway and data -> domain. Dependencies point downward only.
- Keep modules loosely coupled. Layers 3-6 do not import each other; the service layer composes them.
- No business logic in Streamlit UI code. The UI renders and calls services.
- All OpenAI calls go through the LLM gateway in `src/services/llm/`.
- Prefer simple POC solutions over enterprise complexity.

## Dependencies
- Do not add dependencies without a clear need and a note in the ADR log.
- Do not upgrade pinned versions in `requirements.txt` without justification.
- Do not rebuild or reinstall the environment unless something is broken.

## Security and data
- Use configuration and environment variables for secrets (`app/config.py`). Never hard-code secrets.
- Never commit secrets or `.env`. Never print or log keys.
- Never use real customer PII. Synthetic data only, marked as synthetic.

## AI and domain rules
- The human underwriter is responsible for the final loan decision. Never implement autonomous approval or rejection.
- Calculations (DTI, LTV, sums, threshold comparisons) are done in code, never by the LLM.
- Preserve source evidence (document, page, quote) for every AI-generated conclusion.
- Label output as `extracted`, `calculated` or `ai_generated`.
- When evidence is missing, conflicting or unverified, set `requires_human_review`. Say "not found" rather than guess.

## Testing
- Every feature has tests. Follow BUILD -> TEST -> VERIFY -> MOVE FORWARD.
- Run the full suite (`.venv\Scripts\python.exe -m pytest`) after each implementation and report the real result. Do not claim success if tests fail.
- Default tests must not call the network; use FakeLLM and temporary stores.

## Workflow
- Work one roadmap prompt at a time; do not implement ahead of the current prompt.
- Document significant architectural changes.
- Use a feature branch and small, clear commits; do not commit unless asked.
