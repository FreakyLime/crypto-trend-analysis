import pytest
from unittest.mock import patch, MagicMock
from services.gpt_analysis_service import GPTAnalysisService
from config.settings import OPENAI_API_KEY

@patch("services.symbol_analysis_service.SymbolAnalysisService.analyze_symbol")
def test_analyze_symbols_success(mock_analyze_symbol):
    mock_analyze_symbol.side_effect = lambda symbol, *args: {"symbol": symbol, "price": 100} if symbol == "BTCUSDT" else None
    symbols = ["BTCUSDT", "ETHUSDT"]
    mock_binance_client = MagicMock()
    mock_coingecko_data = {}
    service = GPTAnalysisService(api_key=OPENAI_API_KEY)
    result = service.analyze_symbols(symbols, mock_binance_client, mock_coingecko_data)
    assert len(result) == 1
    assert result[0]["symbol"] == "BTCUSDT"
    assert result[0]["price"] == 100
    mock_analyze_symbol.assert_called()

@patch("services.symbol_analysis_service.SymbolAnalysisService.analyze_symbol", side_effect=Exception("Analysis error"))
@patch("services.gpt_analysis_service.logger.error")
def test_analyze_symbols_with_error(mock_logger, mock_analyze_symbol):
    symbols = ["BTCUSDT"]
    mock_binance_client = MagicMock()
    mock_coingecko_data = {}
    service = GPTAnalysisService(api_key=OPENAI_API_KEY)
    result = service.analyze_symbols(symbols, mock_binance_client, mock_coingecko_data)
    assert len(result) == 0
    mock_logger.assert_called_once_with("Error analyzing BTCUSDT: Analysis error", exc_info=True)

def test_prepare_gpt_input():
    global_metrics = {"fear_greed": 50, "btc_dominance": 60.5}
    bitcoin_sentiment = "positive"
    significant_symbols = [
        {"symbol": "BTCUSDT", "price": 100, "rsi": 30, "macd": 1, "signal": 1.5, "bollinger_upper": 110,
         "bollinger_lower": 90, "vwap": 105, "atr": 10, "obv": 1200, "stochastic": 50, "adx": 25,
         "bid_ask_spread": 2, "order_book_imbalance": 0.6, "volume": 1000, "liquidity": 500}
    ]
    service = GPTAnalysisService(api_key=OPENAI_API_KEY)
    result = service.prepare_gpt_input(global_metrics, bitcoin_sentiment, significant_symbols)
    assert "Global Market Metrics:" in result
    assert "Fear & Greed Index: 50" in result
    assert "BTC Dominance: 60.5%" in result
    assert "BTCUSDT | Price: 100 | RSI: 30" in result

@patch("services.gpt_analysis_service.OpenAIClient")
def test_analyze_with_openai_success(mock_openai_utils):
    mock_instance = mock_openai_utils.return_value
    mock_instance.analyze_data.return_value = ("Buy", "Reasoning for BTCUSDT")
    input_text = "Test GPT input"
    service = GPTAnalysisService(api_key=OPENAI_API_KEY)
    suggestion, reasoning = service.analyze_with_openai(input_text)
    assert suggestion == "Buy"
    assert reasoning == "Reasoning for BTCUSDT"
    mock_instance.analyze_data.assert_called_once_with(input_text)

@patch("services.gpt_analysis_service.OpenAIClient")
@patch("services.gpt_analysis_service.logger.error")
def test_analyze_with_openai_exception(mock_logger, mock_openai_utils):
    mock_instance = mock_openai_utils.return_value
    mock_instance.analyze_data.side_effect = Exception("API error")
    input_text = "Test GPT input"
    service = GPTAnalysisService(api_key=OPENAI_API_KEY)
    with pytest.raises(Exception, match="API error"):
        service.analyze_with_openai(input_text)
    mock_logger.assert_called_once_with("Error during GPT analysis.", exc_info=True)