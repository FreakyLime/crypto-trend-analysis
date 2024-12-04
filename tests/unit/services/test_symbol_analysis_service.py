import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from services.symbol_analysis_service import SymbolAnalysisService
from data_fetching.binance_client import BinanceClient
from data_fetching.coingecko_client import CoinGeckoClient

@patch("services.symbol_analysis_service.BINANCE_TO_COINGECKO_SYMBOLS", {"BTCUSDT": "bitcoin"})
@patch("services.symbol_analysis_service.calculate_rsi")
@patch("services.symbol_analysis_service.calculate_macd")
@patch("services.symbol_analysis_service.calculate_bollinger_bands")
@patch("services.symbol_analysis_service.calculate_vwap")
@patch("services.symbol_analysis_service.calculate_atr")
@patch("services.symbol_analysis_service.calculate_obv")
@patch("services.symbol_analysis_service.calculate_stochastic_oscillator")
@patch("services.symbol_analysis_service.calculate_adx")
@patch("services.symbol_analysis_service.calculate_bid_ask_spread")
@patch("services.symbol_analysis_service.calculate_order_book_imbalance")
def test_analyze_symbol_success(
    mock_order_book_imbalance,
    mock_bid_ask_spread,
    mock_adx,
    mock_stochastic,
    mock_obv,
    mock_atr,
    mock_vwap,
    mock_bollinger_bands,
    mock_macd,
    mock_rsi
):
    mock_binance_client = MagicMock(spec=BinanceClient)
    historical_data = pd.DataFrame({
        "open": [100, 102],
        "high": [105, 110],
        "low": [95, 100],
        "close": [103, 106],
        "volume": [1000, 2000]
    })
    mock_binance_client.fetch_historical_data.return_value = historical_data
    mock_binance_client.fetch_order_book.return_value = {"bids": [[100, 1]], "asks": [[102, 1]]}
    mock_binance_client.fetch_volume.return_value = 1000
    mock_binance_client.fetch_liquidity.return_value = 500

    coingecko_data = {"bitcoin": {"usd": 45000, "usd_market_cap": 800_000_000}}

    mock_rsi.return_value = pd.Series([30, 40])
    mock_macd.return_value = (pd.Series([1, 2]), pd.Series([1.5, 2.5]))
    mock_bollinger_bands.return_value = (pd.Series([110, 120]), pd.Series([90, 100]))
    mock_vwap.return_value = pd.Series([102, 105])
    mock_atr.return_value = pd.Series([10, 12])
    mock_obv.return_value = pd.Series([1000, 1200])
    mock_stochastic.return_value = pd.Series([50, 60])
    mock_adx.return_value = pd.Series([25, 30])
    mock_bid_ask_spread.return_value = 2
    mock_order_book_imbalance.return_value = 0.6

    service = SymbolAnalysisService(mock_binance_client, coingecko_data)
    result = service.analyze_symbol("BTCUSDT")

    assert result is not None
    assert result["symbol"] == "BTCUSDT"
    assert result["price"] == 106
    assert result["rsi"] == 40
    assert result["macd"] == 2
    assert result["signal"] == 2.5
    assert result["bollinger_upper"] == 120
    assert result["bollinger_lower"] == 100
    assert result["vwap"] == 105
    assert result["atr"] == 12
    assert result["obv"] == 1200
    assert result["stochastic"] == 60
    assert result["adx"] == 30
    assert result["volume"] == 1000
    assert result["liquidity"] == 500
    assert result["order_book_imbalance"] == 0.6
    assert result["bid_ask_spread"] == 2
    assert result["coingecko_price"] == 45000
    assert result["coingecko_market_cap"] == 800_000_000

@patch("services.symbol_analysis_service.BINANCE_TO_COINGECKO_SYMBOLS", {"BTCUSDT": "bitcoin"})
def test_analyze_symbol_missing_historical_data():
    mock_binance_client = MagicMock(spec=BinanceClient)
    mock_binance_client.fetch_historical_data.return_value = None

    service = SymbolAnalysisService(mock_binance_client, {})
    result = service.analyze_symbol("BTCUSDT")

    assert result is None

@patch("services.symbol_analysis_service.BINANCE_TO_COINGECKO_SYMBOLS", {"BTCUSDT": "bitcoin"})
def test_analyze_symbol_exception():
    mock_binance_client = MagicMock(spec=BinanceClient)
    mock_binance_client.fetch_historical_data.side_effect = Exception("Some error")

    service = SymbolAnalysisService(mock_binance_client, {})
    with pytest.raises(RuntimeError, match="Error analyzing symbol BTCUSDT: Some error"):
        service.analyze_symbol("BTCUSDT")