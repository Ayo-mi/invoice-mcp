from app.schemas import ExtractInvoiceFieldsInput, ExtractInvoiceFieldsOutput
from app.services.parser import parse_invoice_text


def handle_extract_invoice_fields(payload: ExtractInvoiceFieldsInput) -> ExtractInvoiceFieldsOutput:
    parsed = parse_invoice_text(payload.invoice_text)
    return ExtractInvoiceFieldsOutput(
        invoice_id=parsed.invoice_id,
        vendor=parsed.vendor,
        amount=parsed.amount,
        currency=parsed.currency,
        date=parsed.invoice_date.isoformat() if parsed.invoice_date else None,
        line_items=parsed.line_items,
    )

