import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BinanceClient:
    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {"X-MBX-APIKEY": self.api_key}

    def _fetch_data(self, endpoint, params):
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Binance endpoint {endpoint}: {e}")
            return None

    def fetch_historical_data(self, symbol, interval="15m", limit=50):
        logger.info(f"Fetching historical data for {symbol} (Interval: {interval}, Limit: {limit}).")
        data = self._fetch_data("/klines", {"symbol": symbol, "interval": interval, "limit": limit})
        if data:
            return self._parse_historical_data(data)
        return None

    def fetch_volume(self, symbol):
        logger.info(f"Fetching 24-hour trading volume for {symbol}.")
        data = self._fetch_data("/ticker/24hr", {"symbol": symbol})
        return float(data.get("volume", 0)) if data else 0

    def fetch_liquidity(self, symbol):
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
        logger.info(f"Fetching order book for {symbol}.")
        return self._fetch_data("/depth", {"symbol": symbol, "limit": 10})

    def _parse_historical_data(self, data):
        if not data:
            logger.warning("No data received for parsing.")
            return None

        try:
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
            df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
            return df
        except Exception as e:
            logger.error(f"Error parsing historical data: {e}")
            return None
