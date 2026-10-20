# Recording steps

Follow this on camera in order. The recording uses only Finder, Terminal, and Visual Studio Code. The last thing on screen is the decision file.

## Before you start recording

Do these off camera:

- Quit Cursor. Leave Insightful running.
- In Finder, press Command-Shift-Period so dotfiles are visible. Move the existing `.env` in `invoice-mcp` to the Desktop. The recording needs to create that file.
- The current virtualenv is Python 3.9. This project requires 3.10 or newer, so the recording recreates it with Homebrew Python 3.12.
- Save these three files on the Desktop. They were drafted with AI before the recording.

`duplicate.txt`

```text
Invoice ID: INV-202
Vendor: Acme Corp
Date: 2026-04-10
Total: $100.00
```

`price-spike.txt`

```text
Invoice ID: INV-203
Vendor: Acme Corp
Date: 2026-04-12
Total: $140.00
```

`new-vendor.txt`

```text
Invoice ID: INV-300
Vendor: New Vendor LLC
Date: 2026-04-18
Total: $50.00
```

Say this once at the start: "The three invoice texts were drafted with AI before this recording. I am not using an AI assistant during the task."

## 1. Finder — create the environment file

Open `invoice-mcp`. Select `.env.example`, choose File → Duplicate, and rename the copy to `.env`.

Say that the server reads the database location and the port from this file, and the defaults are SQLite and port 8000.

## 2. Terminal — install, migrate, and start the server

Open Terminal, then run:

```bash
cd /Users/ayo/repo/ayo-mi/invoice-mcp
rm -rf .venv
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
alembic upgrade head
python -m app.main
```

Say that the old virtualenv was Python 3.9, which cannot install this project, so you are recreating it with Python 3.12. Leave this tab running.

Open a second tab with Shell → New Tab. In that tab:

```bash
cd /Users/ayo/repo/ayo-mi/invoice-mcp
source .venv/bin/activate
curl -s http://127.0.0.1:8000/health
```

Say that `{"status": "ok", "service": "invoice-mcp"}` means the server is up.

## 3. Terminal — load payment history

In the second tab, paste:

```bash
python << 'PY'
from datetime import date
from app.db.repository import InvoiceRepository
from app.db.session import session_scope

with session_scope() as session:
    repo = InvoiceRepository(session)
    for invoice_id, day in (("INV-100", 1), ("INV-101", 5)):
        repo.add_invoice(
            user_id="user-1",
            vendor="Acme Corp",
            amount=100.0,
            invoice_date=date(2026, 4, day),
            invoice_id=invoice_id,
            currency="USD",
            raw_text="historical invoice",
        )
print("seeded two Acme Corp invoices at $100")
PY
sqlite3 invoice_mcp.db "select invoice_id, vendor, amount, date from invoices;"
```

Say that both saved invoices are Acme Corp for $100, on 1 April and 5 April 2026, for user-1. The duplicate rule matches the same user, vendor, and amount within 30 days. The price rule compares a new amount with that vendor's average.

## 4. Visual Studio Code — check the three invoices

Open the three Desktop files. For each one, point at the invoice id, vendor, amount, and date, and say the parser needs those four lines.

- `duplicate.txt` is Acme Corp for $100 on 10 April, inside the 30-day window.
- `price-spike.txt` is Acme Corp for $140 on 12 April. That is 40% above the $100 average, and the rule flags anything above 30%.
- `new-vendor.txt` is New Vendor LLC. That name is not in the saved payments.

## 5. Terminal — run the three checks

Go back to the second Terminal tab and paste:

```bash
python << 'PY'
import asyncio
from fastmcp import Client

invoices = {
    "duplicate": """
Invoice ID: INV-202
Vendor: Acme Corp
Date: 2026-04-10
Total: $100.00
""",
    "price-spike": """
Invoice ID: INV-203
Vendor: Acme Corp
Date: 2026-04-12
Total: $140.00
""",
    "new-vendor": """
Invoice ID: INV-300
Vendor: New Vendor LLC
Date: 2026-04-18
Total: $50.00
""",
}

async def main():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        for name, text in invoices.items():
            print(f"\n===== {name} =====")
            extracted = await client.call_tool(
                "extract_invoice_fields",
                {"invoice_text": text, "user_id": "user-1"},
            )
            print("fields:", extracted.data)
            vendor = extracted.data["vendor"]
            amount = extracted.data["amount"]
            history = await client.call_tool(
                "compare_invoice_history",
                {"vendor": vendor, "user_id": "user-1", "current_amount": amount},
            )
            print("history:", history.data)
            risk = await client.call_tool(
                "analyze_invoice_risk",
                {"invoice_text": text, "user_id": "user-1"},
            )
            print("risk:", risk.data)

asyncio.run(main())
PY
```

Read each result out loud before you scroll to the next one. Use the numbers the terminal prints if they differ.

- INV-202: history average $100, deviation 0%. Anomaly `duplicate`, risk `high`, recommendation `reject`, confidence about `0.99`. Same vendor, same amount, date within 30 days. A duplicate is high risk, so it is rejected.
- INV-203: average still $100, deviation `40`. Anomaly `price_spike`, risk `medium`, recommendation `review`. Forty percent is over the 30% line, so it is held for review.
- INV-300: average `0`, invoice count `0`. Anomaly `new_vendor`, risk `low`, recommendation `approve`, confidence about `0.7`. The vendor is flagged. A new vendor alone stays low risk. Confidence is lower because there is no history.

## 6. Visual Studio Code — write the decision file

In the project folder, create `invoice-decisions.md` and type the three results you just read:

```markdown
# Invoice payment decisions

User: user-1
Saved history: Acme Corp, two invoices at $100 on 2026-04-01 and 2026-04-05.

| Invoice | Vendor | Amount | Anomalies | Recommendation | Confidence | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| INV-202 | Acme Corp | 100 | duplicate | reject | 0.99 | Same vendor, amount, and a date within 30 days. A duplicate is high risk, so reject. |
| INV-203 | Acme Corp | 140 | price_spike | review | 0.99 | $140 is 40% above the $100 average. Above 30% is medium risk, so review. |
| INV-300 | New Vendor LLC | 50 | new_vendor | approve | 0.70 | No saved payments for this vendor, so it is flagged. New vendor alone stays low risk. Confidence drops because there is no history. |
```

Save the file. This is the file you upload.

## 7. Terminal — run the tests

In the second tab:

```bash
pytest
```

Say that the suite checks the same three outcomes: a duplicate is high risk and reject, a price more than 30% above the vendor average is medium risk and review, and a new vendor is flagged.

Stop the server in the first tab with Control-C. Leave `invoice-decisions.md` open while you end the recording.
