import unittest
from unittest.mock import patch
import requests
from data_fetching.senticrypt_client import SentiCryptClient

class TestSentiCryptClient(unittest.TestCase):
    def setUp(self):
        self.client = SentiCryptClient()

    @patch("data_fetching.senticrypt_client.requests.get")
    def test_fetch_sentiment_success(self, mock_get):
        mock_response = {
            "mean": 0.5,
            "std": 0.1,
            "count": 100
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = self.client.fetch_sentiment()
        self.assertEqual(result, mock_response, "The sentiment data should match the mock response")

    @patch("data_fetching.senticrypt_client.requests.get")
    def test_fetch_sentiment_no_mean(self, mock_get):
        mock_response = {
            "std": 0.1,
            "count": 100
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = self.client.fetch_sentiment()
        self.assertIsNone(result, "The sentiment data should be None when 'mean' is missing")

    @patch("data_fetching.senticrypt_client.requests.get")
    def test_fetch_sentiment_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout

        result = self.client.fetch_sentiment()
        self.assertIsNone(result, "The sentiment data should be None on timeout")

    @patch("data_fetching.senticrypt_client.requests.get")
    def test_fetch_sentiment_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException

        result = self.client.fetch_sentiment()
        self.assertIsNone(result, "The sentiment data should be None on request exception")

    @patch("data_fetching.senticrypt_client.requests.get")
    def test_fetch_sentiment_invalid_json(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

        result = self.client.fetch_sentiment()
        self.assertIsNone(result, "The sentiment data should be None on invalid JSON response")

if __name__ == "__main__":
    unittest.main()