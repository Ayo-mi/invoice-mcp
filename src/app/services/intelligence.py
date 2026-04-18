from app.schemas import Anomaly, Recommendation, RiskLevel

RISK_WEIGHTS = {
    Anomaly.duplicate: 0.7,
    Anomaly.price_spike: 0.3,
    Anomaly.new_vendor: 0.2,
}


def detect_price_spike(amount: float, historical_avg: float) -> bool:
    if historical_avg <= 0:
        return False
    return (amount - historical_avg) / historical_avg > 0.3


def compute_risk_level(anomalies: list[Anomaly]) -> RiskLevel:
    if Anomaly.duplicate in anomalies:
        return RiskLevel.high
    if Anomaly.price_spike in anomalies:
        return RiskLevel.medium
    score = sum(RISK_WEIGHTS.get(anomaly, 0) for anomaly in anomalies)
    if score >= 0.7:
        return RiskLevel.high
    if score >= 0.3:
        return RiskLevel.medium
    return RiskLevel.low


def recommendation_for_risk(risk_level: RiskLevel) -> Recommendation:
    if risk_level == RiskLevel.high:
        return Recommendation.reject
    if risk_level == RiskLevel.medium:
        return Recommendation.review
    return Recommendation.approve


def build_insight(anomalies: list[Anomaly], historical_count: int) -> str:
    if not anomalies and historical_count == 0:
        return "insufficient historical data"
    if not anomalies:
        return "invoice appears consistent with historical patterns"
    labels = ", ".join(a.value for a in anomalies)
    return f"detected anomalies: {labels}"


def compute_confidence(
    *,
    extraction_confidence: float,
    historical_count: int,
    missing_fields: list[str],
) -> float:
    confidence = extraction_confidence
    if historical_count == 0:
        confidence -= 0.3
    confidence -= min(0.2, len(missing_fields) * 0.05)
    return max(0.1, min(0.99, round(confidence, 2)))

