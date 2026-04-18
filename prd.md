# 🧾 Invoice Intelligence MCP Tool (Python)

## Product Requirements Document (PRD) / Software Requirements Specification (SRS)

---

## 1. 🧠 Product Overview

### Goal

Build an MCP server that returns **invoice risk intelligence**, not raw extraction.

### Core Value

> One API call → “Should I approve this invoice?” with risk, insight, and confidence

---

## 2. 🎯 Product Contract (STRICT)

### Surface

- **Primary:** Query
- **Secondary:** Execute

---

### 🔹 Query Endpoint

#### `analyze_invoice_risk`

**Input**

```json
{
  "invoice_text": "string",
  "user_id": "string"
}
```

**Output**

```json
{
  "risk_level": "low | medium | high",
  "anomalies": ["duplicate", "price_spike", "new_vendor"],
  "insight": "string",
  "recommendation": "approve | review | reject",
  "confidence": 0.0,
  "provenance": ["historical_db", "parsed_invoice"],
  "freshness": "real-time"
}
```

### 🔹 Execute Endpoints

#### `extract_invoice_fields`

```json
{
  "invoice_id": "string",
  "vendor": "string",
  "amount": "number",
  "currency": "string",
  "date": "string",
  "line_items": []
}
```

#### `compare_invoice_history`

```json
{
  "average_amount": "number",
  "deviation_percentage": "number",
  "invoice_count": "number"
}
```

---

## 3. 👤 Target User

### Persona

- Finance Manager
- Accountant
- Operations Teams

### Job-to-be-done

Validate invoices before payment.

### Current Pain

- Manual comparison in Excel / QuickBooks
- Duplicate payments
- Missed anomalies

---

## 4. 🚫 Non-Goals

- No dashboards
- No full accounting system
- No complex OCR (v1)
- No contract analysis (future phase)

---

## 5. 🧱 System Architecture

```text
Client → MCP Server → Parser → Intelligence Engine → DB → Response
```

---

## 6. ⚙️ Tech Stack

### Backend

- FastAPI
- Pydantic

### Parsing

- pdfplumber
- regex + heuristics

### Database

- PostgreSQL (prod)
- SQLite (MVP)
- SQLAlchemy

### Optional

- Redis (caching)

---

## 7. 🧩 Core Modules

### 7.1 MCP Server Layer

- Tool definitions
- Schema enforcement
- Request routing

### 7.2 Parsing Layer

**Responsibilities**

Extract:

- `invoice_id`
- `vendor`
- `amount`
- `currency`
- `date`

**Example**

```python
def extract_amount(text: str) -> float:
    import re
    match = re.search(r"(\d+[.,]?\d+)", text)
    return float(match.group(1)) if match else None
```

### 7.3 Intelligence Engine

**Rule 1: Duplicate Detection**

```python
def is_duplicate(invoice, db):
    return db.exists(
        vendor=invoice.vendor,
        amount=invoice.amount,
        date_range=30
    )
```

**Rule 2: Price Spike**

```python
def detect_spike(amount, avg):
    return (amount - avg) / avg > 0.3
```

**Rule 3: New Vendor**

```python
def is_new_vendor(vendor, db):
    return not db.vendor_exists(vendor)
```

### 7.4 Risk Scoring

```python
def compute_risk(flags):
    score = 0
    if "duplicate" in flags:
        score += 0.7
    if "price_spike" in flags:
        score += 0.3
    if "new_vendor" in flags:
        score += 0.2

    if score > 0.7:
        return "high"
    elif score > 0.4:
        return "medium"
    return "low"
```

---

## 8. 🗄️ Database Schema

### `invoices`

- `id`
- `vendor`
- `amount`
- `date`
- `user_id`

### `vendors`

- `name`
- `avg_amount`
- `invoice_count`

---

## 9. ⚡ Performance Requirements

- **Target latency:** < 5 seconds
- **Max limit:** < 60 seconds

### Optimization Strategy

- Precompute vendor averages
- Cache recent invoices
- Avoid heavy runtime computation

---

## 10. 🔌 API Design

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/mcp")
async def handle_mcp(request: dict):
    tool = request.get("tool")

    if tool == "analyze_invoice_risk":
        return analyze_invoice(request["input"])

    elif tool == "extract_invoice_fields":
        return extract_fields(request["input"])
```

---

## 11. 🔐 Context Middleware

```python
def context_middleware(request):
    # Validate auth, origin, etc.
    return True
```

---

## 12. 🧪 Must-Win Test Cases

| Case | Scenario | Expected |
|------|----------|----------|
| 1 | Duplicate invoice | High risk |
| 2 | 40% price spike | Medium risk |
| 3 | New vendor | Flagged |

---

## 13. ⚠️ Edge Cases

### No history

```json
{
  "confidence": 0.4,
  "insight": "insufficient historical data"
}
```

### Partial extraction

- Return null fields
- Lower confidence

### Ambiguous input

- Return minimal insight
- Reduce confidence score

---

## 14. 🚀 Deployment

### Endpoint

`POST /mcp`

### Platforms

- Render
- Railway
- AWS

---

## 15. 💰 Pricing Metadata

```json
{
  "pricing": {
    "executeUsd": "0.001"
  }
}
```

---

## 16. 🧠 Success Criteria

- Returns decision-ready insight
- Deterministic structured JSON
- Sub-5s latency
- Handles incomplete inputs gracefully

---

## 🔥 Cursor Instruction

Build a production-ready MCP server using FastAPI.

**Requirements:**

- Implement `/mcp` endpoint
- Support tools:
  - `analyze_invoice_risk` (Query)
  - `extract_invoice_fields` (Execute)
  - `compare_invoice_history` (Execute)
- Use Pydantic for strict schemas
- Implement parsing layer (regex-based)
- Implement rule-based intelligence engine
- Add PostgreSQL (or SQLite for MVP)
- Ensure responses strictly match schema
- Optimize for <5s latency
- Include test cases for:
  - duplicate detection
  - price spike
  - new vendor
