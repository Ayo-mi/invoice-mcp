from typing import Any
from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from app.handlers.analyze_invoice_risk import handle_analyze_invoice_risk
from app.handlers.compare_invoice_history import handle_compare_invoice_history
from app.handlers.extract_invoice_fields import handle_extract_invoice_fields
from app.schemas import (
    AnalyzeInvoiceRiskInput,
    AnalyzeInvoiceRiskOutput,
    CompareInvoiceHistoryInput,
    CompareInvoiceHistoryOutput,
    ExtractInvoiceFieldsInput,
    ExtractInvoiceFieldsOutput,
)


class ToolRouter:
    def __init__(self, session_factory: Optional[sessionmaker] = None):
        self.session_factory = session_factory

    def analyze_invoice_risk(self, input_data: dict[str, Any]) -> AnalyzeInvoiceRiskOutput:
        payload = AnalyzeInvoiceRiskInput.model_validate(input_data)
        return handle_analyze_invoice_risk(payload, session_factory=self.session_factory)

    def extract_invoice_fields(self, input_data: dict[str, Any]) -> ExtractInvoiceFieldsOutput:
        payload = ExtractInvoiceFieldsInput.model_validate(input_data)
        return handle_extract_invoice_fields(payload)

    def compare_invoice_history(self, input_data: dict[str, Any]) -> CompareInvoiceHistoryOutput:
        payload = CompareInvoiceHistoryInput.model_validate(input_data)
        return handle_compare_invoice_history(payload, session_factory=self.session_factory)

