from app.schemas import Anomaly, RiskLevel
from app.services.intelligence import compute_risk_level, detect_price_spike


def test_compute_risk_level_duplicate_is_high() -> None:
    level = compute_risk_level([Anomaly.duplicate, Anomaly.new_vendor])
    assert level == RiskLevel.high


def test_detect_price_spike_threshold() -> None:
    assert detect_price_spike(amount=140, historical_avg=100) is True
    assert detect_price_spike(amount=125, historical_avg=100) is False

