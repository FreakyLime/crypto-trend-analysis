import unittest
from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

class TestBinance(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.client = Client(api_key=self.api_key, api_secret=self.api_secret)

    def test_ping(self):
        status = self.client.ping()
        self.assertEqual(status, {}, "Ping should return an empty dictionary")

    def test_account_info(self):
        try:
            account_info = self.client.get_account()
            self.assertIn("balances", account_info, "Account info should include 'balances'")
        except Exception as e:
            self.fail(f"Account info retrieval failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
