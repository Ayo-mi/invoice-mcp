import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from app.schemas import ParsedInvoice

INVOICE_ID_PATTERNS = [
    re.compile(r"invoice\s*(?:id|#|number)?\s*[:\-]?\s*([A-Z0-9\-_/]+)", re.IGNORECASE),
]
VENDOR_PATTERNS = [
    re.compile(r"vendor\s*[:\-]\s*([^\n]+)", re.IGNORECASE),
    re.compile(r"from\s*[:\-]\s*([^\n]+)", re.IGNORECASE),
]
AMOUNT_PATTERN = re.compile(r"(?:total|amount\s*due|amount)\s*[:\-]?\s*([$€£]?\s*[\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
DATE_PATTERNS = [
    re.compile(r"date\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE),
    re.compile(r"date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE),
]
LINE_ITEM_PATTERN = re.compile(r"^\s*-\s*(.+?)\s*[:\-]\s*([$€£]?\s*[\d,]+(?:\.\d{1,2})?)\s*$", re.MULTILINE)

CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
}


def _extract_first(text: str, patterns: List[re.Pattern]) -> Optional[str]:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def _parse_amount(raw_amount: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
    if not raw_amount:
        return None, None
    currency = None
    symbol_match = re.match(r"\s*([$€£])", raw_amount)
    if symbol_match:
        currency = CURRENCY_SYMBOLS.get(symbol_match.group(1))
    clean = re.sub(r"[^0-9.]", "", raw_amount)
    try:
        amount = float(clean)
    except ValueError:
        return None, currency
    return amount, currency


def _parse_date(raw_date: Optional[str]) -> Optional[date]:
    if not raw_date:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw_date, fmt).date()
        except ValueError:
            continue
    return None


def _parse_line_items(text: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for description, raw_amount in LINE_ITEM_PATTERN.findall(text):
        amount, currency = _parse_amount(raw_amount)
        item: Dict[str, Any] = {"description": description.strip()}
        if amount is not None:
            item["amount"] = amount
        if currency:
            item["currency"] = currency
        items.append(item)
    return items


def parse_invoice_text(invoice_text: str) -> ParsedInvoice:
    invoice_id = _extract_first(invoice_text, INVOICE_ID_PATTERNS)
    vendor = _extract_first(invoice_text, VENDOR_PATTERNS)
    raw_amount = _extract_first(invoice_text, [AMOUNT_PATTERN])
    raw_date = _extract_first(invoice_text, DATE_PATTERNS)
    amount, currency_from_amount = _parse_amount(raw_amount)
    parsed_date = _parse_date(raw_date)
    line_items = _parse_line_items(invoice_text)

    currency = currency_from_amount
    if not currency:
        explicit_currency = re.search(r"currency\s*[:\-]?\s*([A-Za-z]{3})", invoice_text, re.IGNORECASE)
        currency = explicit_currency.group(1).upper() if explicit_currency else None

    missing_fields = [
        field_name
        for field_name, value in {
            "invoice_id": invoice_id,
            "vendor": vendor,
            "amount": amount,
            "date": parsed_date,
        }.items()
        if value is None
    ]
    extraction_confidence = max(0.3, 1 - (len(missing_fields) * 0.15))

    return ParsedInvoice(
        invoice_id=invoice_id,
        vendor=vendor,
        amount=amount,
        currency=currency,
        invoice_date=parsed_date,
        line_items=line_items,
        extraction_confidence=extraction_confidence,
        missing_fields=missing_fields,
    )

