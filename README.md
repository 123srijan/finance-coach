# Finance Coach

A personal finance dashboard for tracking income and expenses, reviewing spending by category, and getting budget guidance from an AI assistant.

## Features

- Account registration and sign-in
- Income and expense tracking
- Spending summaries by month and category
- Password recovery by email (requires SMTP configuration)
- AI finance chat powered by Gemini (requires a Gemini API key)

## Built with

- Python and FastAPI
- SQLAlchemy and SQLite
- HTML, CSS, and JavaScript
- Google Gemini API

## Run locally

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
