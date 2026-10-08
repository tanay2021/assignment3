# Intelligent Loan Underwriting Assistant

## Business purpose
The Intelligent Loan Underwriting Assistant is a BFSI proof of concept designed to support underwriters by organizing loan-related information, comparing documents, and highlighting inconsistencies while keeping the human reviewer in control of final decisions.

## Current POC stage
The engineering foundation, architecture blueprint, domain models, services and repositories are in place (Prompts 0 to 2). No AI functionality exists yet: document processing, RAG, policy reasoning and the Streamlit screens are added incrementally in later stages. See [docs/implementation_roadmap.md](docs/implementation_roadmap.md).

## Technology stack
- Python 3.11.x
- Streamlit (for future local UI work)
- LangChain and LangGraph (future orchestration foundation)
- OpenAI API (future LLM integration)
- PyMuPDF (future document extraction)
- sentence-transformers (future embeddings)
- ChromaDB (future vector storage)
- SQLite (future local data persistence)
- pytest (testing)
- python-dotenv (environment configuration)
- Python logging (structured application logging)

## Application architecture
Layers depend only downward. The UI never touches data or AI code directly.
```text
app/ui  ->  app/bootstrap  ->  src/services  ->  src/data  ->  src/domain
                |                   |                |
            app/config          src/common <---------+   (shared errors and constants)
```
| Layer | Location | Responsibility |
|---|---|---|
| Presentation | `app/ui/` | Display and input only (placeholder Streamlit entry point) |
| Startup | `app/bootstrap.py`, `app/config.py`, `app/logging_config.py` | Load configuration, set up logging, wire services |
| Application services | `src/services/` | One service per use area; validate input; raise controlled errors |
| Data access | `src/data/` | Repository interfaces and a SQLite implementation |
| Domain models | `src/domain/` | Pydantic data contracts, enums, integrity validation |
| Shared | `src/common/` | Application exceptions and constants |
| Future capabilities | `src/documents/`, `src/rag/`, `src/loan/`, `src/policies/` | Document intelligence, RAG, loan rules, policy reasoning (later prompts) |

Full design: [docs/architecture.md](docs/architecture.md). What is implemented today: [docs/domain_model_implementation.md](docs/domain_model_implementation.md).

## Domain model layer
`src/domain/` holds small Pydantic models for Applicant, LoanApplication, Document, DocumentEvidence, ExtractedInformation, PolicyDocument, PolicyQuery, Inconsistency, UnderwritingSummary and AIResponse, plus controlled enums. Models check data integrity (non-empty ids, non-negative amounts, valid enum values, evidence for AI claims). They contain no underwriting rules, no AI code and no UI code. An underwriting summary can only say `pending_underwriter`; the human makes every loan decision.

## Project structure
```text
loan-processing-ai-poc/
├── app/
│   ├── bootstrap.py          application initialization
│   ├── config.py             settings (the only place environment variables are read)
│   ├── logging_config.py
│   ├── healthcheck.py
│   └── ui/                   placeholder Streamlit entry point
├── src/
│   ├── common/               exceptions, constants
│   ├── domain/               models and enums
│   ├── data/                 repository interfaces, SQLite implementation
│   ├── services/             application services and wiring
│   ├── documents/  rag/  loan/  policies/    reserved for later prompts
├── tests/
│   ├── unit/                 domain, common, data, services, architecture
│   └── integration/
├── data/                     sample_documents/, sample_policies/ (synthetic only)
├── docs/                     architecture and design documents
├── AGENTS.md                 rules for all coding work
├── .env.example  requirements.txt  pytest.ini  run.py  README.md  SETUP.md
└── .venv/
```

## Security baseline
- Never hard-code secrets.
- Never commit `.env` files.
- Never print API keys or sensitive configuration.
- Never store customer or PII data in the repository.
- Use synthetic or sample data only.
- Keep security-sensitive configuration centralized and environment-driven.

## Setup overview
1. Create a Python 3.11 virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and add local values.
4. Run the test suite and health check.
5. Use `run.py` or the project entry point for future app startup.

## Activate the virtual environment
Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run tests
```bash
pytest                         # all tests (offline, no API key needed)
pytest tests/unit/domain       # one area
pytest -k repository           # by name
```
On Windows, if `pytest` is not on your PATH, use `.\.venv\Scripts\python.exe -m pytest`. Tests use in-memory or temporary databases and never touch real data.

## Run the health check
```bash
python run.py --health-check
```

## Start the application when implemented later
```bash
python run.py
```

## Notes
- This project intentionally avoids RAG, AI business logic, and document intelligence in this foundation stage.
- The goal is a stable and testable base for future incremental feature work.
- The dependency set is intentionally small and aligned to the planned architecture.

## Architecture and design documents
Start with [AGENTS.md](AGENTS.md) (rules for all coding work), then the documents in `docs/`:
[business_requirements](docs/business_requirements.md) · [poc_scope](docs/poc_scope.md) · [user_journeys](docs/user_journeys.md) · [architecture](docs/architecture.md) · [data_flow](docs/data_flow.md) · [data_contracts](docs/data_contracts.md) · [ai_capability_mapping](docs/ai_capability_mapping.md) · [rag_design](docs/rag_design.md) · [security_responsible_ai](docs/security_responsible_ai.md) · [test_strategy](docs/test_strategy.md) · [demo_data_strategy](docs/demo_data_strategy.md) · [acceptance_criteria](docs/acceptance_criteria.md) · [implementation_roadmap](docs/implementation_roadmap.md) · [architecture_decisions](docs/architecture_decisions.md)
