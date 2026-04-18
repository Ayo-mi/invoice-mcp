from app.services.parser import parse_invoice_text


def test_parse_invoice_text_extracts_core_fields() -> None:
    text = """
    Invoice ID: INV-999
    Vendor: Acme Corp
    Date: 2026-04-18
    Total: $120.50
    - Service Fee: $100.00
    - Tax: $20.50
    """
    parsed = parse_invoice_text(text)

    assert parsed.invoice_id == "INV-999"
    assert parsed.vendor == "Acme Corp"
    assert parsed.amount == 120.50
    assert parsed.currency == "USD"
    assert parsed.invoice_date is not None
    assert len(parsed.line_items) == 2
    assert parsed.extraction_confidence > 0.7


def test_parse_invoice_text_handles_partial_input() -> None:
    text = "Vendor: Acme Corp"
    parsed = parse_invoice_text(text)

    assert parsed.vendor == "Acme Corp"
    assert parsed.amount is None
    assert "amount" in parsed.missing_fields
    assert parsed.extraction_confidence < 1

