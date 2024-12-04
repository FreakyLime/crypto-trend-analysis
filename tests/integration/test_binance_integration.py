import unittest
from dotenv import load_dotenv
import os
from data_fetching.binance_client import BinanceClient

load_dotenv()

class TestBinance(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.client = BinanceClient(api_key=self.api_key, api_secret=self.api_secret)

    def test_ping(self):
        status = self.client._fetch_data("/ping", {})
        self.assertEqual(status, {}, "Ping should return an empty dictionary")

    def test_fetch_volume(self):
        volume = self.client.fetch_volume("BTCUSDT")
        self.assertIsInstance(volume, float, "Volume should be a float")

    def test_fetch_order_book(self):
        order_book = self.client.fetch_order_book("BTCUSDT")
        self.assertIsNotNone(order_book, "Order book should not be None")
        self.assertIn("bids", order_book, "Order book should include 'bids'")
        self.assertIn("asks", order_book, "Order book should include 'asks'")

if __name__ == "__main__":
    unittest.main()