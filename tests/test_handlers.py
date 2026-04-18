from app.router import ToolRouter
from app.schemas import Recommendation, RiskLevel


def _invoice_text(*, invoice_id: str, vendor: str, date: str, total: float) -> str:
    return f"""
    Invoice ID: {invoice_id}
    Vendor: {vendor}
    Date: {date}
    Total: ${total}
    """


def test_duplicate_detection_is_high_risk(seeded_session_factory) -> None:
    router = ToolRouter(session_factory=seeded_session_factory)
    result = router.analyze_invoice_risk(
        {
            "invoice_text": _invoice_text(
                invoice_id="INV-202",
                vendor="Acme Corp",
                date="2026-04-10",
                total=100.0,
            ),
            "user_id": "user-1",
        }
    )
    assert result.risk_level == RiskLevel.high
    assert Recommendation.reject == result.recommendation
    assert "duplicate" in [a.value for a in result.anomalies]


def test_price_spike_is_medium_risk(seeded_session_factory) -> None:
    router = ToolRouter(session_factory=seeded_session_factory)
    result = router.analyze_invoice_risk(
        {
            "invoice_text": _invoice_text(
                invoice_id="INV-203",
                vendor="Acme Corp",
                date="2026-04-12",
                total=140.0,
            ),
            "user_id": "user-1",
        }
    )
    assert result.risk_level == RiskLevel.medium
    assert result.recommendation == Recommendation.review
    assert "price_spike" in [a.value for a in result.anomalies]


def test_new_vendor_is_flagged(router) -> None:
    result = router.analyze_invoice_risk(
        {
            "invoice_text": _invoice_text(
                invoice_id="INV-300",
                vendor="New Vendor LLC",
                date="2026-04-18",
                total=50.0,
            ),
            "user_id": "user-1",
        }
    )
    assert "new_vendor" in [a.value for a in result.anomalies]


def test_compare_invoice_history_contract(seeded_session_factory) -> None:
    router = ToolRouter(session_factory=seeded_session_factory)
    result = router.compare_invoice_history(
        {"vendor": "Acme Corp", "user_id": "user-1", "current_amount": 140}
    )
    assert result.average_amount == 100.0
    assert result.invoice_count >= 2
    assert result.deviation_percentage == 40.0

