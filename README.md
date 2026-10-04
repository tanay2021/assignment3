# Intelligent Loan Underwriting Assistant

## Business purpose
The Intelligent Loan Underwriting Assistant is a BFSI proof of concept designed to support underwriters by organizing loan-related information, comparing documents, and highlighting inconsistencies while keeping the human reviewer in control of final decisions.

## Current POC stage
This stage establishes the engineering foundation. AI functionality will be implemented incrementally in subsequent development stages.

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

## Project structure
```text
loan-processing-ai-poc/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── healthcheck.py
│   └── logging_config.py
├── src/
│   ├── __init__.py
│   ├── documents/
│   ├── rag/
│   ├── loan/
│   ├── policies/
│   └── services/
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── data/
│   ├── sample_documents/
│   └── sample_policies/
├── logs/
├── docs/
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
├── README.md
├── SETUP.md
├── run.py
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
pytest
```

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
