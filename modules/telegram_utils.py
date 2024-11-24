import httpx
import logging

logger = logging.getLogger(__name__)

class TelegramUtils:
    def __init__(self, bot_token):
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(self, chat_id, text, parse_mode=None):
        """
        Send a message to a Telegram chat.
        """
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10)
                response.raise_for_status()
                logger.info("Message sent to Telegram successfully!")
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"HTTP Request Error: {e}")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Status Error: {e.response.text}")
            return None  # Ensure `None` is returned on failure
