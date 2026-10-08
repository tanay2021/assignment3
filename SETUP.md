# Setup Guide

## A. Prerequisites
Before starting, make sure the following are installed on your machine:
- Python 3.11.x
- Git
- VS Code or another editor
- A terminal with access to the project folder

## B. Python verification
Confirm Python is installed and available on your PATH:

Windows PowerShell:
```powershell
python --version
```

Linux/macOS:
```bash
python3 --version
```

Expected result: Python 3.11.x.

## C. Git verification
Confirm Git is installed:

```bash
git --version
```

If Git is missing, install it before continuing.

## D. Virtual environment creation
Create a project-local virtual environment:

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

## E. Dependency installation
From the project root:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## F. Environment variable setup
Copy the example file and populate local values:

```bash
copy .env.example .env
```

Linux/macOS:
```bash
cp .env.example .env
```

Then edit `.env` with your local values. Keep the file local and never commit it.

## G. API key configuration instructions
The project foundation supports future OpenAI use but does not require a real key for local testing at this stage.

Example:
```env
OPENAI_API_KEY=
APP_ENV=development
LOG_LEVEL=INFO
```

When a real API key is needed later:
1. Create or retrieve the key from your provider.
2. Store it only in `.env` on your local machine.
3. Ensure `.env` remains in `.gitignore`.
4. Never print it or commit it to source control.

## H. Test execution
Run the full test suite:

```bash
pytest
```

Expected successful output includes a summary similar to:
```text
6 passed in X.XXs
```

## I. Health check execution
Validate the environment and foundation setup:

```bash
python run.py --health-check
```

Expected successful output includes:
```text
Python version: 3.11.x
Environment: development
Log level: INFO
Health check passed: the project foundation is ready for incremental development.
```

## J. Troubleshooting
- If `python` points to the wrong version, use `py -3.11` on Windows or `python3.11` on Unix-like systems.
- If packages fail to install, upgrade `pip` first and verify you are in the virtual environment.
- If pytest cannot find modules, verify the project root is active and the `pythonpath = .` setting in `pytest.ini` is present.
- If logging fails, check that the `logs` directory is writable.
- If `.env` values are not picked up, ensure the file is named exactly `.env` and the project root is the active working directory.

## K. Expected successful output
A healthy environment should show:
- Python 3.11.x is active
- Dependencies install cleanly
- `pytest` passes
- The health check reports a passing status
- Logging creates a `logs/application.log` file
- No secrets are exposed in terminal output or repository files

## Important note
This setup is intentionally minimal and platform-aware. Docker is not required for the local POC foundation.

## Optional: database location
The application stores loan records in SQLite. By default the file is `data/loan_poc.sqlite3` (git-ignored). To change it, set `DATABASE_PATH` in `.env`. No OpenAI API key is needed at this stage.
