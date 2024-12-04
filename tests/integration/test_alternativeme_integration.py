import unittest
from unittest.mock import patch
import requests
from data_fetching.alternativeme_client import AlternativeMeClient

class TestAlternativeMeClient(unittest.TestCase):
    def setUp(self):
        self.client = AlternativeMeClient()

    @patch("data_fetching.alternativeme_client.requests.get")
    def test_fetch_fear_and_greed_success(self, mock_get):
        mock_response = {
            "data": [
                {"value": "45", "value_classification": "Fear", "timestamp": "1633024800"}
            ],
            "metadata": {
                "error": None
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = self.client.fetch_fear_and_greed()
        self.assertEqual(result, 45, "The Fear & Greed Index should be 45")

    @patch("data_fetching.alternativeme_client.requests.get")
    def test_fetch_fear_and_greed_no_data(self, mock_get):
        mock_response = {"data": []}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = self.client.fetch_fear_and_greed()
        self.assertIsNone(result, "The Fear & Greed Index should be None when no data is available")

    @patch("data_fetching.alternativeme_client.requests.get")
    def test_fetch_fear_and_greed_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout

        result = self.client.fetch_fear_and_greed()
        self.assertIsNone(result, "The Fear & Greed Index should be None on timeout")

    @patch("data_fetching.alternativeme_client.requests.get")
    def test_fetch_fear_and_greed_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException

        result = self.client.fetch_fear_and_greed()
        self.assertIsNone(result, "The Fear & Greed Index should be None on request exception")

if __name__ == "__main__":
    unittest.main()