import pytest
import pandas as pd
import numpy as np
from analysis.technical_indicators.trend_indicators import calculate_adx

def test_calculate_adx():
    # Mock input data
    data = pd.DataFrame({
        "high": [45, 46, 47, 48, 49, 50, 51, 50, 49, 48, 47],
        "low": [40, 41, 42, 43, 44, 45, 46, 45, 44, 43, 42],
        "close": [42, 44, 45, 46, 48, 47, 50, 49, 48, 47, 46]
    })

    # Call the function
    adx = calculate_adx(data, period=3)

    # Assert the result is not None
    assert adx is not None, "ADX should not be None"

    # Assert the result has the same length as input data
    assert len(adx) == len(data), "ADX output length mismatch"

    # Assert that the result contains NaN for the initial `period - 1` values
    assert adx[:2].isnull().all(), "Initial ADX values should be NaN"

    # Assert the actual values against expected ones
    expected_adx = [np.nan, np.nan, np.nan, np.nan, np.nan, 100.0, 100.0, 77.78, 55.56, 55.56, 77.78]
    np.testing.assert_almost_equal(
        adx[~adx.isnull()].values,  # Ignore NaN values during comparison
        np.array(expected_adx)[~np.isnan(expected_adx)],  # Ignore NaN values from expected
        decimal=1,
        err_msg="ADX calculation is incorrect"
    )
