# Invoice MCP

Invoice Intelligence MCP server built with FastMCP, SQLAlchemy, and Alembic.

## Features

- Query tool: `analyze_invoice_risk`
- Execute tools: `extract_invoice_fields`, `compare_invoice_history`
- Strict Pydantic schemas with deterministic outputs
- Regex invoice parsing + rule-based anomaly detection
- SQLite by default, PostgreSQL-ready via `DATABASE_URL`
- Alembic migrations for schema lifecycle

## System Prompt Artifact

Builder prompt is tracked in:
- `docs/system-prompts/invoice-mcp-builder.md`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Database Migrations (Alembic)

Create a new revision:

```bash
alembic revision --autogenerate -m "describe change"
```

Upgrade to latest migration:

```bash
alembic upgrade head
```

Downgrade by one revision:

```bash
alembic downgrade -1
```

## Run

```bash
python -m app.main
```

Server defaults:
- MCP endpoint: `http://127.0.0.1:8000/mcp`
- Health route: `http://127.0.0.1:8000/health`

## Test

```bash
pytest
```

