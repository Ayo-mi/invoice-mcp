from datetime import date
from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from app.db.repository import InvoiceRepository
from app.db.session import session_scope
from app.schemas import AnalyzeInvoiceRiskInput, AnalyzeInvoiceRiskOutput, Anomaly, Freshness
from app.services.intelligence import (
    build_insight,
    compute_confidence,
    compute_risk_level,
    detect_price_spike,
    recommendation_for_risk,
)
from app.services.parser import parse_invoice_text


def handle_analyze_invoice_risk(
    payload: AnalyzeInvoiceRiskInput,
    *,
    session_factory: Optional[sessionmaker] = None,
) -> AnalyzeInvoiceRiskOutput:
    parsed = parse_invoice_text(payload.invoice_text)
    anomalies: list[Anomaly] = []
    vendor = parsed.vendor or "unknown_vendor"
    amount = parsed.amount or 0.0
    invoice_date = parsed.invoice_date or date.today()

    with session_scope(session_factory) as session:
        repo = InvoiceRepository(session)
        historical_avg, historical_count = repo.get_invoice_history(user_id=payload.user_id, vendor=vendor)

        if amount > 0 and repo.is_duplicate(
            user_id=payload.user_id,
            vendor=vendor,
            amount=amount,
            invoice_date=invoice_date,
        ):
            anomalies.append(Anomaly.duplicate)

        if amount > 0 and detect_price_spike(amount, historical_avg):
            anomalies.append(Anomaly.price_spike)

        if not repo.vendor_exists(user_id=payload.user_id, vendor=vendor):
            anomalies.append(Anomaly.new_vendor)

        if parsed.vendor and parsed.amount and parsed.invoice_date:
            repo.add_invoice(
                user_id=payload.user_id,
                vendor=parsed.vendor,
                amount=parsed.amount,
                invoice_date=parsed.invoice_date,
                invoice_id=parsed.invoice_id,
                currency=parsed.currency,
                raw_text=payload.invoice_text,
            )

    risk_level = compute_risk_level(anomalies)
    recommendation = recommendation_for_risk(risk_level)
    confidence = compute_confidence(
        extraction_confidence=parsed.extraction_confidence,
        historical_count=historical_count,
        missing_fields=parsed.missing_fields,
    )

    return AnalyzeInvoiceRiskOutput(
        risk_level=risk_level,
        anomalies=anomalies,
        insight=build_insight(anomalies, historical_count),
        recommendation=recommendation,
        confidence=confidence,
        provenance=["historical_db", "parsed_invoice"],
        freshness=Freshness.real_time,
    )

