# Finance Coach
Features

- Sign up, sign in, sign out, and password recovery by email
- Record income and expenses with dates and categories
- Review monthly income, expenses, net balance, and spending by category
- Search and filter transactions through the API
- Import transactions from a bounded CSV file
- Ask Gemini for budgeting guidance based on aggregate dashboard totals
- English and Hindi interface
- SQLite storage for local development

## Stack

- Python 3.11
- FastAPI and Uvicorn
- SQLAlchemy and SQLite
- Vanilla HTML, CSS, and JavaScript
- Google Gemini API (optional)

## Run locally

In PowerShell, open the repository folder and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Open <http://127.0.0.1:8001/dashboard>. The local SQLite database is created in the repository directory when the app starts.

The dashboard and account features work without Gemini or SMTP. Add the relevant values to `.env` to enable AI chat and password recovery. Never commit `.env` or real API credentials.

## Configuration

See [.env.example](.env.example) for the available settings. For a hosted deployment, set a long random `SESSION_SECRET_KEY`, use HTTPS with `COOKIE_SECURE=true`, configure `APP_PUBLIC_URL`, and provide SMTP settings before enabling password recovery.

## CSV format

CSV import expects the columns `date`, `description`, `amount`, and `category_id`. Dates use `YYYY-MM-DD`. Leave `category_id` blank for an uncategorized transaction. An optional `is_income` column accepts `true`, `yes`, or `1` for income. Imports are limited to 5 MB and 5,000 rows.

## Security and privacy

- Account routes require a signed, HTTP-only session cookie.
- Finance records are filtered by the signed-in account.
- CSV imports validate rows and category IDs before saving.
- AI requests use aggregate totals only; individual descriptions are not sent.
- Run behind HTTPS in production and keep secrets out of source control.

This project is an educational budgeting tool. Its summaries and AI responses are not financial, investment, or tax advice.

## Project layout

```text
app/
  main.py             Authentication, dashboard, and AI endpoints
  models.py           SQLAlchemy data models
  database.py         SQLite engine and sessions
  routers/            Transaction, category, and insight endpoints
  security.py         Password hashing and signed sessions
  static/index.html   Responsive dashboard and sign-in interface
```

## CI

GitHub Actions installs project dependencies and checks Python syntax on Python 3.11 and 3.12.
