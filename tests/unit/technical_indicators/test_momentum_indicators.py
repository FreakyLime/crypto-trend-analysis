import pytest
import pandas as pd
from analysis.technical_indicators.momentum_indicators import calculate_rsi, calculate_macd, calculate_stochastic_oscillator

@pytest.fixture
def sample_data():
    data = {
        "close": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        "low": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        "high": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    }
    return pd.DataFrame(data)

def test_calculate_rsi(sample_data):
    rsi = calculate_rsi(sample_data)
    assert rsi is not None, "RSI should not be None"
    assert len(rsi) == len(sample_data), "RSI length should match data length"

def test_calculate_macd(sample_data):
    macd, signal = calculate_macd(sample_data)
    assert macd is not None, "MACD should not be None"
    assert signal is not None, "Signal should not be None"
    assert len(macd) == len(sample_data), "MACD length should match data length"
    assert len(signal) == len(sample_data), "Signal length should match data length"

def test_calculate_stochastic_oscillator(sample_data):
    stochastic = calculate_stochastic_oscillator(sample_data)
    assert stochastic is not None, "Stochastic Oscillator should not be None"
    assert len(stochastic) == len(sample_data), "Stochastic Oscillator length should match data length"

if __name__ == "__main__":
    pytest.main()