import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BinanceUtils:
    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "X-MBX-APIKEY": self.api_key
        }

    def fetch_historical_data(self, symbol, interval="15m", limit=50):
        """
        Fetch historical candlestick data for a symbol.
        """
        endpoint = f"{self.BASE_URL}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        try:
            logger.info(f"Fetching historical data for {symbol}...")
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._parse_historical_data(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

    def fetch_volume(self, symbol):
        """
        Fetch 24-hour trading volume for a symbol.
        """
        endpoint = f"{self.BASE_URL}/ticker/24hr"
        params = {"symbol": symbol}
        try:
            logger.info(f"Fetching volume for {symbol}...")
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data.get("volume", 0))
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching volume for {symbol}: {e}")
            return 0

    def fetch_liquidity(self, symbol):
        """
        Fetch the bid/ask spread as a proxy for liquidity.
        """
        endpoint = f"{self.BASE_URL}/depth"
        params = {"symbol": symbol, "limit": 5}
        try:
            logger.info(f"Fetching liquidity for {symbol}...")
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            if bids and asks:
                highest_bid = float(bids[0][0])
                lowest_ask = float(asks[0][0])
                return round(abs(lowest_ask - highest_bid), 6)
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching liquidity for {symbol}: {e}")
            return None

    def fetch_order_book(self, symbol):
        """
        Fetch the order book for a symbol.
        """
        endpoint = f"{self.BASE_URL}/depth"
        params = {"symbol": symbol, "limit": 10}
        try:
            logger.info(f"Fetching order book for {symbol}...")
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return None

    def _parse_historical_data(self, data):
        """
        Convert Binance historical candlestick data into a pandas DataFrame.
        """
        try:
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            logger.info("Historical data parsed successfully into DataFrame.")
            return df
        except Exception as e:
            logger.error(f"Error parsing historical data into DataFrame: {e}")
            return None
