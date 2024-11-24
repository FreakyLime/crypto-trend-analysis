import time
import requests
import logging

logger = logging.getLogger(__name__)
COINGECKO_PRICE_API = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_DOMINANCE_API = "https://api.coingecko.com/api/v3/global"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CryptoMonitor/1.0)"}

def fetch_all_coin_data(crypto_ids, currency='usd', delay=1.5, max_retries=3):
    """
    Fetch data for multiple cryptocurrencies from CoinGecko in batches.
    
    Args:
        crypto_ids (list): List of CoinGecko IDs (e.g., ['bitcoin', 'ethereum']).
        currency (str): Target currency (default: 'usd').
        delay (float): Delay between batch requests.
        max_retries (int): Maximum number of retries for failed requests.

    Returns:
        dict: Consolidated data for all cryptocurrencies or None on failure.
    """
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
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Fetching batch: {batch} (Attempt {attempt}/{max_retries})")
                response = requests.get(COINGECKO_PRICE_API, params=params, headers=HEADERS, timeout=10)
                response.raise_for_status()
                data = response.json()
                all_data.update(data)
                logger.info(f"Successfully fetched batch: {batch}")
                break  # Exit retry loop on success
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching batch {batch}: {e}")
                if attempt == max_retries:
                    logger.error(f"Failed to fetch batch {batch} after {max_retries} attempts.")
                else:
                    time.sleep(delay)  # Delay before retrying
        time.sleep(delay)  # Delay between batches

    return all_data

def fetch_bitcoin_dominance(delay=1.5, max_retries=3):
    """
    Fetch Bitcoin dominance from the CoinGecko API with retries and rate limiting.
    
    Args:
        delay (float): Delay between retries or requests.
        max_retries (int): Maximum number of retries for failed requests.

    Returns:
        float: Bitcoin dominance or None on failure.
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Fetching Bitcoin dominance (Attempt {attempt}/{max_retries})")
            response = requests.get(COINGECKO_DOMINANCE_API, headers=HEADERS, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            data = response.json()
            btc_dominance = data.get("data", {}).get("market_cap_percentage", {}).get("btc")
            if btc_dominance is not None:
                logger.info(f"Bitcoin dominance fetched successfully: {btc_dominance}%")
                return btc_dominance
            else:
                logger.warning("Bitcoin dominance not found in the API response.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Bitcoin dominance: {e}")
            if attempt == max_retries:
                logger.error(f"Failed to fetch Bitcoin dominance after {max_retries} attempts.")
                return None
            else:
                time.sleep(delay)  # Delay before retrying
    return None
