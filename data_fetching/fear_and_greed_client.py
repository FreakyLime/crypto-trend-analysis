import requests
import logging

logger = logging.getLogger(__name__)

FEAR_GREED_API = "https://api.alternative.me/fng/"

def fetch_fear_and_greed():
    """
    Fetch the Crypto Fear & Greed Index from the Alternative.me API.
    """
    try:
        logger.info(f"Fetching Fear & Greed Index from {FEAR_GREED_API}")
        response = requests.get(FEAR_GREED_API, timeout=10)
        response.raise_for_status()  # Raise error for HTTP codes 4xx/5xx
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
