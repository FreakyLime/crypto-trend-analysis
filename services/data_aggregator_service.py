from data_fetching.alternativeme_client import AlternativeMeClient
from data_fetching.coingecko_client import CoinGeckoClient
from data_fetching.senticrypt_client import SentiCryptClient
import logging

logger = logging.getLogger()

class DataAggregatorService:
    def __init__(self):
        self.alternative_me_client = AlternativeMeClient()
        self.coingecko_client = CoinGeckoClient()
        self.senticrypt_client = SentiCryptClient()

    def fetch_global_metrics(self):
        try:
            fear_greed = self.alternative_me_client.fetch_fear_and_greed()
            btc_dominance = self.coingecko_client.fetch_bitcoin_dominance()
            logger.info("Successfully fetched global metrics.")
            return {"fear_greed": fear_greed, "btc_dominance": btc_dominance}
        except Exception as e:
            logger.error(f"Error fetching global metrics: {e}", exc_info=True)
            return {"fear_greed": None, "btc_dominance": None}

    def fetch_sentiment(self, symbol):
        try:
            if symbol == "BTCUSDT":
                sentiment = self.senticrypt_client.fetch_sentiment()
                logger.info(f"Successfully fetched sentiment for {symbol}.")
                return sentiment
            else:
                logger.info(f"Sentiment data not available for {symbol}.")
                return None
        except Exception as e:
            logger.error(f"Error fetching sentiment for {symbol}: {e}", exc_info=True)
            return None

    def fetch_coingecko_data(self, symbols, mapping):
        try:
            crypto_ids = [mapping[symbol] for symbol in symbols if symbol in mapping]
            if not crypto_ids:
                logger.error("No valid symbols found in mapping.")
                return None
            data = self.coingecko_client.fetch_all_coin_data(crypto_ids)
            logger.info(f"Successfully fetched CoinGecko data for symbols: {symbols}.")
            return data
        except KeyError as e:
            logger.error(f"Mapping error: Missing symbol in mapping. {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}", exc_info=True)
            return None