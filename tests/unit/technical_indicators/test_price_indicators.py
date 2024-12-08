import pytest
from analysis.technical_indicators.price_indicators import calculate_bid_ask_spread

def test_calculate_bid_ask_spread():
    # Test case with valid order book
    order_book = {
        "bids": [["100.0", "1"], ["99.0", "2"]],
        "asks": [["101.0", "1"], ["102.0", "2"]]
    }
    spread = calculate_bid_ask_spread(order_book)
    assert spread is not None, "Spread should not be None"
    assert spread == 1.0, "Spread should be 1.0"

    # Test case with empty bids
    order_book = {
        "bids": [],
        "asks": [["101.0", "1"], ["102.0", "2"]]
    }
    spread = calculate_bid_ask_spread(order_book)
    assert spread is None, "Spread should be None when bids are empty"

    # Test case with empty asks
    order_book = {
        "bids": [["100.0", "1"], ["99.0", "2"]],
        "asks": []
    }
    spread = calculate_bid_ask_spread(order_book)
    assert spread is None, "Spread should be None when asks are empty"

    # Test case with invalid data
    order_book = {
        "bids": [["invalid", "1"], ["99.0", "2"]],
        "asks": [["101.0", "1"], ["102.0", "2"]]
    }
    spread = calculate_bid_ask_spread(order_book)
    assert spread is None, "Spread should be None when data is invalid"

if __name__ == "__main__":
    pytest.main()