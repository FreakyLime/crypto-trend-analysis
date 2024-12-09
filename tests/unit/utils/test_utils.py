import pytest
import json
from utils.utils import split_reasoning_by_symbol

def test_split_reasoning_by_symbol_json():
    reasoning = json.dumps({
        "BTC": "Buy BTC because of strong fundamentals.",
        "ETH": "Sell ETH due to market conditions."
    })
    symbols = ["BTC", "ETH", "XRP"]
    result = split_reasoning_by_symbol(reasoning, symbols)
    assert result["BTC"] == "Buy BTC because of strong fundamentals."
    assert result["ETH"] == "Sell ETH due to market conditions."
    assert result["XRP"] is None

def test_split_reasoning_by_symbol_text():
    reasoning = "'BTC': 'Buy BTC because of strong fundamentals.', 'ETH': 'Sell ETH due to market conditions.'"
    symbols = ["BTC", "ETH", "XRP"]
    result = split_reasoning_by_symbol(reasoning, symbols)
    assert result["BTC"] == "Buy BTC because of strong fundamentals."
    assert result["ETH"] == "Sell ETH due to market conditions."
    assert result["XRP"] is None

def test_split_reasoning_by_symbol_invalid_json():
    reasoning = "Invalid JSON"
    symbols = ["BTC", "ETH", "XRP"]
    result = split_reasoning_by_symbol(reasoning, symbols)
    assert result["BTC"] is None
    assert result["ETH"] is None
    assert result["XRP"] is None

def test_split_reasoning_by_symbol_partial_match():
    reasoning = json.dumps({
        "BTC": "Buy BTC because of strong fundamentals."
    })
    symbols = ["BTC", "ETH"]
    result = split_reasoning_by_symbol(reasoning, symbols)
    assert result["BTC"] == "Buy BTC because of strong fundamentals."
    assert result["ETH"] is None