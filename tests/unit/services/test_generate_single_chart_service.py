import pytest
import pandas as pd
from unittest.mock import patch
from services.chart_generator_service import generate_single_chart  # Corrected import path

@patch("services.chart_generator_service.plt.savefig")  # Mock plt.savefig
@patch("services.chart_generator_service.os.makedirs")  # Mock os.makedirs
def test_generate_single_chart_success(mock_makedirs, mock_savefig):
    # Test data
    data = {
        "open_time": [1660000000000, 1660003600000, 1660007200000],
        "open": [100, 102, 105],
        "high": [105, 107, 110],
        "low": [95, 100, 103],
        "close": [103, 106, 108],
        "volume": [1000, 1200, 900],
    }
    df = pd.DataFrame(data)

    # Test parameters
    symbol = "BTCUSD"
    candlestick_interval = "1h"
    output_dir = "test_charts"

    # Call the function
    result = generate_single_chart(symbol, df, candlestick_interval, output_dir)

    # Assertions
    mock_makedirs.assert_called_once()
    mock_savefig.assert_called_once()
    assert result is not None
    assert symbol in result
