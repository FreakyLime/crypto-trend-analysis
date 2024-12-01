import pytest
from unittest.mock import patch, MagicMock
from services.data_aggregator_service import fetch_global_metrics, fetch_sentiment, fetch_coingecko_data

@patch("services.data_aggregator_service.fetch_bitcoin_dominance")
@patch("services.data_aggregator_service.fetch_fear_and_greed")
def test_fetch_global_metrics_success(mock_fetch_fear_and_greed, mock_fetch_bitcoin_dominance):
    # Mock return values
    mock_fetch_fear_and_greed.return_value = 45
    mock_fetch_bitcoin_dominance.return_value = 60.5

    # Call the function
    result = fetch_global_metrics()

    # Assertions
    assert result == {"fear_greed": 45, "btc_dominance": 60.5}
    mock_fetch_fear_and_greed.assert_called_once()
    mock_fetch_bitcoin_dominance.assert_called_once()


@patch("services.data_aggregator_service.fetch_fear_and_greed", side_effect=Exception("API Error"))
@patch("services.data_aggregator_service.fetch_bitcoin_dominance", side_effect=Exception("API Error"))
@patch("services.data_aggregator_service.logger.error")
def test_fetch_global_metrics_failure(mock_logger, mock_fetch_fear_and_greed, mock_fetch_bitcoin_dominance):
    # Call the function
    result = fetch_global_metrics()

    # Assertions
    assert result == {"fear_greed": None, "btc_dominance": None}
    mock_logger.assert_called()  # Ensure logger.error was called


@patch("services.data_aggregator_service.fetch_sentiment_from_senticrypt")
def test_fetch_sentiment_success(mock_fetch_sentiment_from_senticrypt):
    # Mock return value
    mock_fetch_sentiment_from_senticrypt.return_value = {"sentiment": "positive"}

    # Call the function for BTCUSDT
    result = fetch_sentiment("BTCUSDT")

    # Assertions
    assert result == {"sentiment": "positive"}
    mock_fetch_sentiment_from_senticrypt.assert_called_once()


@patch("services.data_aggregator_service.logger.info")
def test_fetch_sentiment_symbol_not_supported(mock_logger):
    # Call the function for a non-supported symbol
    result = fetch_sentiment("ETHUSDT")

    # Assertions
    assert result is None
    mock_logger.assert_called_with("Sentiment data not available for ETHUSDT.")


@patch("services.data_aggregator_service.fetch_all_coin_data")
def test_fetch_coingecko_data_success(mock_fetch_all_coin_data):
    # Mock return value
    mock_fetch_all_coin_data.return_value = {"bitcoin": {"price": 45000}}

    # Symbol mapping
    symbols = ["BTCUSDT"]
    mapping = {"BTCUSDT": "bitcoin"}

    # Call the function
    result = fetch_coingecko_data(symbols, mapping)

    # Assertions
    assert result == {"bitcoin": {"price": 45000}}
    mock_fetch_all_coin_data.assert_called_once_with(["bitcoin"])


@patch("services.data_aggregator_service.logger.error")
def test_fetch_coingecko_data_key_error(mock_logger):
    # Symbol mapping with missing symbol
    symbols = ["BTCUSDT"]
    mapping = {}

    # Call the function
    result = fetch_coingecko_data(symbols, mapping)

    # Assertions
    assert result is None  # Or {} depending on your preferred behavior
    mock_logger.assert_called()  # Ensure logger.error was called


@patch("services.data_aggregator_service.fetch_all_coin_data", side_effect=Exception("API Error"))
@patch("services.data_aggregator_service.logger.error")
def test_fetch_coingecko_data_exception(mock_logger, mock_fetch_all_coin_data):
    # Symbol mapping
    symbols = ["BTCUSDT"]
    mapping = {"BTCUSDT": "bitcoin"}

    # Call the function
    result = fetch_coingecko_data(symbols, mapping)

    # Assertions
    assert result is None
    mock_logger.assert_called()  # Ensure logger.error was called for Exception
