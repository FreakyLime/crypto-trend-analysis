from data_fetching.fear_and_greed_client import fetch_fear_and_greed
from data_fetching.coingecko_client import fetch_all_coin_data, fetch_bitcoin_dominance
from data_fetching.senticrypt_client import fetch_sentiment_from_senticrypt
import logging

logger = logging.getLogger(__name__)

def fetch_global_metrics():
    """Fetch global cryptocurrency metrics like Fear & Greed index and Bitcoin dominance."""
    try:
        fear_greed = fetch_fear_and_greed()
        btc_dominance = fetch_bitcoin_dominance()
        logger.info("Successfully fetched global metrics.")
        return {"fear_greed": fear_greed, "btc_dominance": btc_dominance}
    except Exception as e:
        logger.error(f"Error fetching global metrics: {e}", exc_info=True)
        return {"fear_greed": None, "btc_dominance": None}

def fetch_sentiment(symbol):
    """Fetch sentiment for a given symbol. Currently supports only BTCUSDT."""
    try:
        if symbol == "BTCUSDT":
            sentiment = fetch_sentiment_from_senticrypt()
            logger.info(f"Successfully fetched sentiment for {symbol}.")
            return sentiment
        else:
            logger.info(f"Sentiment data not available for {symbol}.")
            return None
    except Exception as e:
        logger.error(f"Error fetching sentiment for {symbol}: {e}", exc_info=True)
        return None

def fetch_coingecko_data(symbols, mapping):
    """Fetch cryptocurrency data from CoinGecko for the provided symbols."""
    try:
        crypto_ids = [mapping[symbol] for symbol in symbols if symbol in mapping]
        if not crypto_ids:  # Handle empty list case
            logger.error("No valid symbols found in mapping.")
            return None
        data = fetch_all_coin_data(crypto_ids)
        logger.info(f"Successfully fetched CoinGecko data for symbols: {symbols}.")
        return data
    except KeyError as e:
        logger.error(f"Mapping error: Missing symbol in mapping. {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching CoinGecko data: {e}", exc_info=True)
        return None

