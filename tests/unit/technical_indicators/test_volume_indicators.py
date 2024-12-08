import pytest
import pandas as pd
from analysis.technical_indicators.volume_indicators import calculate_obv, calculate_order_book_imbalance, calculate_vwap

@pytest.fixture
def sample_data():
    data = {
        "close": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        "volume": [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_order_book():
    return {
        "bids": [["100.0", "1"], ["99.0", "2"]],
        "asks": [["101.0", "1"], ["102.0", "2"]]
    }

def test_calculate_obv(sample_data):
    obv = calculate_obv(sample_data)
    assert obv is not None, "OBV should not be None"
    assert len(obv) == len(sample_data), "OBV length should match data length"

def test_calculate_order_book_imbalance(sample_order_book):
    imbalance = calculate_order_book_imbalance(sample_order_book)
    assert imbalance is not None, "Order book imbalance should not be None"
    assert 0 <= imbalance <= 1, "Order book imbalance should be between 0 and 1"

def test_calculate_vwap(sample_data):
    vwap = calculate_vwap(sample_data)
    assert vwap is not None, "VWAP should not be None"
    assert len(vwap) == len(sample_data), "VWAP length should match data length"

if __name__ == "__main__":
    pytest.main()