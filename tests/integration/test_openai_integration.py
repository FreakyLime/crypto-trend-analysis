import unittest
import openai
from dotenv import load_dotenv
import os

load_dotenv()

class TestOpenAI(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def test_chat_completion(self):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello!"}],
                max_tokens=5
            )
            self.assertIn("choices", response, "Response should include 'choices'")
        except Exception as e:
            self.fail(f"OpenAI ChatCompletion failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
