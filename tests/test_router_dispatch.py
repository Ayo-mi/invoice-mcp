from app.router import ToolRouter


def test_router_dispatches_all_tools(router: ToolRouter) -> None:
    extract = router.extract_invoice_fields(
        {
            "invoice_text": "Invoice ID: INV-1\nVendor: Acme\nDate: 2026-04-18\nTotal: $10.00",
            "user_id": "user-1",
        }
    )
    assert extract.invoice_id == "INV-1"

    history = router.compare_invoice_history({"vendor": "Acme", "user_id": "user-1"})
    assert history.invoice_count >= 0

    risk = router.analyze_invoice_risk(
        {
            "invoice_text": "Invoice ID: INV-2\nVendor: NewCo\nDate: 2026-04-18\nTotal: $50.00",
            "user_id": "user-1",
        }
    )
    assert risk.risk_level.value in {"low", "medium", "high"}

