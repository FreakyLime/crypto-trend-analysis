import requests
import datetime
import logging

logger = logging.getLogger(__name__)

def fetch_sentiment_from_senticrypt():
    """
    Fetch Bitcoin sentiment data from SentiCrypt API for the current date.
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Get current date in YYYY-MM-DD format
    url = f"https://api.senticrypt.com/v2/history/{current_date}.json"
    try:
        logger.info(f"Fetching Bitcoin sentiment data for {current_date} from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for HTTP codes 4xx/5xx
        sentiment_data = response.json()

        # Validate and return the sentiment data
        if "mean" in sentiment_data:
            logger.info(f"Bitcoin sentiment data fetched successfully: {sentiment_data}")
            return sentiment_data
        else:
            logger.warning(f"Unexpected sentiment data format for {current_date}: {sentiment_data}")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"Request to SentiCrypt API timed out for {current_date}.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Bitcoin sentiment data: {e}")
        return None
    except ValueError as e:
        logger.error(f"Invalid JSON response from SentiCrypt for {current_date}: {e}")
        return None
