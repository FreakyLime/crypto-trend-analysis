import unittest
from dotenv import load_dotenv
import os
from data_fetching.openai_client import OpenAIClient

load_dotenv()

class TestOpenAI(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAIClient(api_key=self.api_key)

    def test_analyze_data(self):
        try:
            input_text = "What is the current sentiment on Bitcoin?"
            suggestion, analysis = self.client.analyze_data(input_text)
            self.assertIsInstance(suggestion, str, "Suggestion should be a string")
            self.assertIsInstance(analysis, str, "Analysis should be a string")
        except Exception as e:
            self.fail(f"OpenAI analyze_data failed with error: {e}")

if __name__ == "__main__":
    unittest.main()