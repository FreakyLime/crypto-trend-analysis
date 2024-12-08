import pytest
import pandas as pd
from analysis.technical_indicators.volatility_indicators import calculate_bollinger_bands, calculate_atr

@pytest.fixture
def sample_data():
    data = {
        "close": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        "high": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
        "low": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    }
    return pd.DataFrame(data)

def test_calculate_bollinger_bands(sample_data):
    upper_band, lower_band = calculate_bollinger_bands(sample_data)
    assert upper_band is not None, "Upper Bollinger Band should not be None"
    assert lower_band is not None, "Lower Bollinger Band should not be None"
    assert len(upper_band) == len(sample_data), "Upper Bollinger Band length should match data length"
    assert len(lower_band) == len(sample_data), "Lower Bollinger Band length should match data length"

def test_calculate_atr(sample_data):
    atr = calculate_atr(sample_data)
    assert atr is not None, "ATR should not be None"
    assert len(atr) == len(sample_data), "ATR length should match data length"

if __name__ == "__main__":
    pytest.main()