from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Recommendation(str, Enum):
    approve = "approve"
    review = "review"
    reject = "reject"


class Anomaly(str, Enum):
    duplicate = "duplicate"
    price_spike = "price_spike"
    new_vendor = "new_vendor"


class Freshness(str, Enum):
    real_time = "real-time"


class AnalyzeInvoiceRiskInput(StrictModel):
    invoice_text: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class ExtractInvoiceFieldsInput(StrictModel):
    invoice_text: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class CompareInvoiceHistoryInput(StrictModel):
    vendor: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    current_amount: Optional[float] = Field(default=None, ge=0)


class ExtractInvoiceFieldsOutput(StrictModel):
    invoice_id: Optional[str] = None
    vendor: Optional[str] = None
    amount: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = None
    date: Optional[str] = None
    line_items: list[dict[str, Any]] = Field(default_factory=list)


class CompareInvoiceHistoryOutput(StrictModel):
    average_amount: float = Field(ge=0)
    deviation_percentage: float
    invoice_count: int = Field(ge=0)


class AnalyzeInvoiceRiskOutput(StrictModel):
    risk_level: RiskLevel
    anomalies: list[Anomaly]
    insight: str
    recommendation: Recommendation
    confidence: float = Field(ge=0, le=1)
    provenance: list[str]
    freshness: Freshness


class ParsedInvoice(StrictModel):
    invoice_id: Optional[str] = None
    vendor: Optional[str] = None
    amount: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = None
    invoice_date: Optional[date] = None
    line_items: list[dict[str, Any]] = Field(default_factory=list)
    extraction_confidence: float = Field(default=0.7, ge=0, le=1)
    missing_fields: list[str] = Field(default_factory=list)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: Optional[str]) -> Optional[str]:
        return value.upper() if value else value

