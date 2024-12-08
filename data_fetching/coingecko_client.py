import time
import requests
import logging

logger = logging.getLogger()

class CoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"
    HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CryptoMonitor/1.0)"}

    def __init__(self, config=None):
        if config:
            self.BASE_URL = config.get("BASE_URL", self.BASE_URL)
            self.HEADERS = config.get("HEADERS", self.HEADERS)

    def _fetch_data(self, endpoint, params=None, delay=1.5, max_retries=3):
        url = f"{self.BASE_URL}{endpoint}"
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, params=params, headers=self.HEADERS, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching data from {url}: {e}")
                if attempt == max_retries:
                    logger.error(f"Failed to fetch data from {url} after {max_retries} attempts.")
                    return None
                time.sleep(delay)
        return None

    def fetch_all_coin_data(self, crypto_ids, currency='usd', delay=1.5, max_retries=3):
        batch_size = 100
        all_data = {}
        for i in range(0, len(crypto_ids), batch_size):
            batch = crypto_ids[i:i + batch_size]
            params = {
                "ids": ",".join(batch),
                "vs_currencies": currency,
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            data = self._fetch_data("/simple/price", params, delay, max_retries)
            if data:
                all_data.update(data)
            time.sleep(delay)
        return all_data

    def fetch_bitcoin_dominance(self, delay=1.5, max_retries=3):
        data = self._fetch_data("/global", delay=delay, max_retries=max_retries)
        if data:
            btc_dominance = data.get("data", {}).get("market_cap_percentage", {}).get("btc")
            if btc_dominance is not None:
                return btc_dominance
            logger.warning("Bitcoin dominance not found in the API response.")
        return None
