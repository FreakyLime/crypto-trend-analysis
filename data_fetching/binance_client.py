import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BinanceUtils:
    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, api_key, api_secret):
        """
        Initialize BinanceUtils with API credentials.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {"X-MBX-APIKEY": self.api_key}

    def _fetch_data(self, endpoint, params):
        """
        Helper method to make API requests.
        
        Args:
            endpoint (str): API endpoint.
            params (dict): Query parameters for the API request.

        Returns:
            dict: Parsed JSON response from the API.
        """
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Binance endpoint {endpoint}: {e}")
            return None

    def fetch_historical_data(self, symbol, interval="15m", limit=50):
        """
        Fetch historical candlestick data for a given symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT").
            interval (str): Candlestick interval (e.g., "15m").
            limit (int): Number of data points to fetch.

        Returns:
            pd.DataFrame: Historical data as a pandas DataFrame, or None if the request fails.
        """
        logger.info(f"Fetching historical data for {symbol} (Interval: {interval}, Limit: {limit}).")
        data = self._fetch_data("/klines", {"symbol": symbol, "interval": interval, "limit": limit})
        if data:
            return self._parse_historical_data(data)
        return None

    def fetch_volume(self, symbol):
        """
        Fetch the 24-hour trading volume for a given symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT").

        Returns:
            float: 24-hour trading volume, or 0 if the request fails.
        """
        logger.info(f"Fetching 24-hour trading volume for {symbol}.")
        data = self._fetch_data("/ticker/24hr", {"symbol": symbol})
        return float(data.get("volume", 0)) if data else 0

    def fetch_liquidity(self, symbol):
        """
        Fetch liquidity by calculating the bid-ask spread for a given symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT").

        Returns:
            float: Liquidity (bid-ask spread), or None if the request fails.
        """
        logger.info(f"Fetching liquidity (bid/ask spread) for {symbol}.")
        data = self._fetch_data("/depth", {"symbol": symbol, "limit": 5})
        if data:
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            if bids and asks:
                highest_bid = float(bids[0][0])
                lowest_ask = float(asks[0][0])
                return round(abs(lowest_ask - highest_bid), 6)
            logger.info(f"No sufficient data to calculate liquidity for {symbol}.")
        return None

    def fetch_order_book(self, symbol):
        """
        Fetch the order book for a given symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT").

        Returns:
            dict: Order book data, or None if the request fails.
        """
        logger.info(f"Fetching order book for {symbol}.")
        return self._fetch_data("/depth", {"symbol": symbol, "limit": 10})

    def _parse_historical_data(self, data):
        """
        Parse raw candlestick data into a pandas DataFrame.

        Args:
            data (list): Raw candlestick data.

        Returns:
            pd.DataFrame: Parsed data as a DataFrame, or None if parsing fails.
        """
        if not data:
            logger.warning("No data received for parsing.")
            return None

        try:
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            # Convert data to appropriate types
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
            df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
            return df
        except Exception as e:
            logger.error(f"Error parsing historical data: {e}")
            return None
