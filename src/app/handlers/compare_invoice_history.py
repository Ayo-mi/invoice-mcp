from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from app.db.repository import InvoiceRepository
from app.db.session import session_scope
from app.schemas import CompareInvoiceHistoryInput, CompareInvoiceHistoryOutput


def handle_compare_invoice_history(
    payload: CompareInvoiceHistoryInput,
    *,
    session_factory: Optional[sessionmaker] = None,
) -> CompareInvoiceHistoryOutput:
    with session_scope(session_factory) as session:
        repo = InvoiceRepository(session)
        avg_amount, count = repo.get_invoice_history(user_id=payload.user_id, vendor=payload.vendor)
    current_amount = payload.current_amount if payload.current_amount is not None else avg_amount
    deviation_percentage = 0.0
    if avg_amount > 0:
        deviation_percentage = ((current_amount - avg_amount) / avg_amount) * 100
    return CompareInvoiceHistoryOutput(
        average_amount=round(avg_amount, 2),
        deviation_percentage=round(deviation_percentage, 2),
        invoice_count=count,
    )

