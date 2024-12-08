import pytest
from unittest.mock import Mock
from data_fetching.coingecko_client import CoinGeckoClient

@pytest.fixture
def client():
    return CoinGeckoClient()

def test_fetch_all_coin_data(client, mocker):
    mock_response = {
        "bitcoin": {
            "usd": 50000,
            "usd_market_cap": 1_000_000_000,
            "usd_24h_vol": 50_000_000
        },
        "ethereum": {
            "usd": 4000,
            "usd_market_cap": 500_000_000,
            "usd_24h_vol": 30_000_000
        }
    }
    mocker.patch('requests.get', return_value=Mock(status_code=200, json=lambda: mock_response))
    
    crypto_ids = ["bitcoin", "ethereum"]
    data = client.fetch_all_coin_data(crypto_ids)
    assert data is not None, "Data should not be None"
    assert "bitcoin" in data, "Bitcoin data should be in the response"
    assert "ethereum" in data, "Ethereum data should be in the response"
    assert data["bitcoin"]["usd"] == 50000, "Bitcoin price should match mock response"
    assert data["ethereum"]["usd"] == 4000, "Ethereum price should match mock response"

def test_fetch_bitcoin_dominance(client, mocker):
    mock_response = {
        "data": {
            "market_cap_percentage": {
                "btc": 60.5
            }
        }
    }
    mocker.patch('requests.get', return_value=Mock(status_code=200, json=lambda: mock_response))
    
    btc_dominance = client.fetch_bitcoin_dominance()
    assert btc_dominance is not None, "Bitcoin dominance should not be None"
    assert btc_dominance == 60.5, "Bitcoin dominance should match the mock response"

def test_fetch_data_failure(client, mocker):
    mocker.patch('requests.get', return_value=Mock(status_code=500, json=lambda: None))
    
    data = client._fetch_data("/simple/price")
    assert data is None, "Data should be None when the API fails"

