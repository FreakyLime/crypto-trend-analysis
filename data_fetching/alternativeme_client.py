import requests
import logging

logger = logging.getLogger(__name__)

class AlternativeMeClient:
    BASE_URL = "https://api.alternative.me/fng/"

    def __init__(self):
        pass

    def fetch_fear_and_greed(self):
        try:
            logger.info(f"Fetching Fear & Greed Index from {self.BASE_URL}")
            response = requests.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data and "data" in data and len(data["data"]) > 0:
                fear_greed_value = int(data["data"][0]["value"])
                logger.info(f"Fear & Greed Index fetched successfully: {fear_greed_value}")
                return fear_greed_value
            else:
                logger.warning("Fear & Greed Index data is missing or invalid.")
                return None
        except requests.exceptions.Timeout:
            logger.error("Request to Fear & Greed API timed out.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            return None