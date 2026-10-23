import pytest

def test_central_bank_catalyst_weighting():
    """Verify catalyst window scaling factor logic for central bank event windows."""
    base_vol_forecast = 0.12
    catalyst_event_multiplier = 1.35  # High-impact central bank window (e.g., FOMC / ECB / SARB)
    adjusted_vol = base_vol_forecast * catalyst_event_multiplier
    
    assert pytest.approx(adjusted_vol, 0.001) == 0.162
    assert adjusted_vol > base_vol_forecast

def test_implied_vol_basis_point_spread():
    """Verify basis point spread calculation between market IV and model forecast."""
    market_iv = 0.1500  # 15.00% Implied Volatility
    model_forecast_vol = 0.1350  # 13.50% Forecasted Realized Volatility
    bps_spread = (market_iv - model_forecast_vol) * 10000
    
    assert pytest.approx(bps_spread, 0.1) == 150.0  # 150 bps spread (Rich IV)
