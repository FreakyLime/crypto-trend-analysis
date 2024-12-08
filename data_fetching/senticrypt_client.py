import requests
import datetime
import logging

logger = logging.getLogger()

class SentiCryptClient:
    BASE_URL = "https://api.senticrypt.com/v2/history"

    def fetch_sentiment(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        previous_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        def fetch_for_date(date):
            url = f"{self.BASE_URL}/{date}.json"
            try:
                logger.info(f"Fetching Bitcoin sentiment data for {date} from {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                sentiment_data = response.json()

                if "mean" in sentiment_data:
                    logger.info(f"Bitcoin sentiment data fetched successfully: {sentiment_data}")
                    return sentiment_data
                else:
                    logger.warning(f"Unexpected sentiment data format for {date}: {sentiment_data}")
                    return None
            except requests.exceptions.Timeout:
                logger.error(f"Request to SentiCrypt API timed out for {date}.")
                return None
            except requests.exceptions.RequestException as e:
                if response.status_code == 404:
                    logger.warning(f"Data not found for {date}. Trying previous date.")
                    return None
                logger.error(f"Error fetching Bitcoin sentiment data: {e}")
                return None
            except ValueError as e:
                logger.error(f"Invalid JSON response from SentiCrypt for {date}: {e}")
                return None

        sentiment_data = fetch_for_date(current_date)
        if sentiment_data is None:
            sentiment_data = fetch_for_date(previous_date)

        return sentiment_data