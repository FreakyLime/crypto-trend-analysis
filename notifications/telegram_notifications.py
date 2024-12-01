import logging
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

async def send_analysis_to_telegram_with_image(bot_token, chat_id, message, image_path):
    """
    Sends a message with an image to a specified Telegram chat.

    Args:
        bot_token (str): The Telegram bot API token.
        chat_id (str): The Telegram chat ID to send the message to.
        message (str): The message text to send with the image.
        image_path (str): The file path of the image to send.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    bot = Bot(token=bot_token)
    try:
        with open(image_path, 'rb') as image_file:
            await bot.send_photo(chat_id=chat_id, photo=image_file, caption=message)
            logger.info(f"Successfully sent image to Telegram chat {chat_id}.")
            return True
    except TelegramError as e:
        logger.error(f"Telegram API error while sending image to chat {chat_id}: {e}")
        # Fallback to text-only message
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Sent text-only fallback message to Telegram chat {chat_id}.")
            return True
        except TelegramError as te:
            logger.error(f"Failed to send fallback message to Telegram chat {chat_id}: {te}")
            return False
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}.")
        # Notify about missing image
        try:
            await bot.send_message(chat_id=chat_id, text=f"{message}\n\n⚠️ Image file not found: {image_path}")
            return True
        except TelegramError as te:
            logger.error(f"Failed to send fallback message about missing image to Telegram chat {chat_id}: {te}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error while sending image to Telegram chat {chat_id}: {e}", exc_info=True)
        # Fallback message for unexpected errors
        try:
            await bot.send_message(chat_id=chat_id, text=f"{message}\n\n⚠️ An unexpected error occurred.")
            return True
        except TelegramError as te:
            logger.error(f"Failed to send fallback message about unexpected error to Telegram chat {chat_id}: {te}")
            return False
