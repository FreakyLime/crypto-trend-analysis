import unittest
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class TestTelegramBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Set up the Telegram bot and environment variables
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = Bot(token=self.bot_token)

    async def test_send_message(self):
        # Test sending a message using the Telegram bot
        try:
            response = await self.bot.send_message(chat_id=self.chat_id, text="This is a test message from unittest!")
            self.assertIsNotNone(response, "Response from Telegram should not be None")
            self.assertEqual(response.chat.id, int(self.chat_id), "Message should be sent to the correct chat ID")
        except Exception as e:
            self.fail(f"Sending message failed with error: {e}")

    async def asyncTearDown(self):
        # Clean up if needed
        pass

if __name__ == "__main__":
    unittest.main()
