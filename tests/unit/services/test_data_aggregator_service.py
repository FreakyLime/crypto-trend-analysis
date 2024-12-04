import pytest
from unittest.mock import patch, MagicMock
from services.data_aggregator_service import DataAggregatorService

@patch("services.data_aggregator_service.CoinGeckoClient.fetch_bitcoin_dominance")
@patch("services.data_aggregator_service.AlternativeMeClient.fetch_fear_and_greed")
def test_fetch_global_metrics_success(mock_fetch_fear_and_greed, mock_fetch_bitcoin_dominance):
    mock_fetch_fear_and_greed.return_value = 45
    mock_fetch_bitcoin_dominance.return_value = 60.5
    service = DataAggregatorService()
    result = service.fetch_global_metrics()
    assert result == {"fear_greed": 45, "btc_dominance": 60.5}
    mock_fetch_fear_and_greed.assert_called_once()
    mock_fetch_bitcoin_dominance.assert_called_once()

@patch("services.data_aggregator_service.AlternativeMeClient.fetch_fear_and_greed", side_effect=Exception("API Error"))
@patch("services.data_aggregator_service.CoinGeckoClient.fetch_bitcoin_dominance", side_effect=Exception("API Error"))
@patch("services.data_aggregator_service.logger.error")
def test_fetch_global_metrics_failure(mock_logger, mock_fetch_fear_and_greed, mock_fetch_bitcoin_dominance):
    service = DataAggregatorService()
    result = service.fetch_global_metrics()
    assert result == {"fear_greed": None, "btc_dominance": None}
    mock_logger.assert_called()

@patch("services.data_aggregator_service.SentiCryptClient.fetch_sentiment")
def test_fetch_sentiment_success(mock_fetch_sentiment):
    mock_fetch_sentiment.return_value = {"sentiment": "positive"}
    service = DataAggregatorService()
    result = service.fetch_sentiment("BTCUSDT")
    assert result == {"sentiment": "positive"}
    mock_fetch_sentiment.assert_called_once()

@patch("services.data_aggregator_service.logger.info")
def test_fetch_sentiment_symbol_not_supported(mock_logger):
    service = DataAggregatorService()
    result = service.fetch_sentiment("ETHUSDT")
    assert result is None
    mock_logger.assert_called_with("Sentiment data not available for ETHUSDT.")

@patch("services.data_aggregator_service.CoinGeckoClient.fetch_all_coin_data")
def test_fetch_coingecko_data_success(mock_fetch_all_coin_data):
    mock_fetch_all_coin_data.return_value = {"bitcoin": {"price": 45000}}
    symbols = ["BTCUSDT"]
    mapping = {"BTCUSDT": "bitcoin"}
    service = DataAggregatorService()
    result = service.fetch_coingecko_data(symbols, mapping)
    assert result == {"bitcoin": {"price": 45000}}
    mock_fetch_all_coin_data.assert_called_once_with(["bitcoin"])

@patch("services.data_aggregator_service.logger.error")
def test_fetch_coingecko_data_key_error(mock_logger):
    symbols = ["BTCUSDT"]
    mapping = {}
    service = DataAggregatorService()
    result = service.fetch_coingecko_data(symbols, mapping)
    assert result is None
    mock_logger.assert_called()

@patch("services.data_aggregator_service.CoinGeckoClient.fetch_all_coin_data", side_effect=Exception("API Error"))
@patch("services.data_aggregator_service.logger.error")
def test_fetch_coingecko_data_exception(mock_logger, mock_fetch_all_coin_data):
    symbols = ["BTCUSDT"]
    mapping = {"BTCUSDT": "bitcoin"}
    service = DataAggregatorService()
    result = service.fetch_coingecko_data(symbols, mapping)
    assert result is None
    mock_logger.assert_called()