import logging
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger()

async def send_analysis_to_telegram_with_image(bot_token, chat_id, message, image_path):
    bot = Bot(token=bot_token)
    try:
        with open(image_path, 'rb') as image_file:
            await bot.send_photo(chat_id=chat_id, photo=image_file, caption=message)
            logger.info(f"Successfully sent image to Telegram chat {chat_id}.")
            return True
    except TelegramError as e:
        logger.error(f"Telegram API error while sending image to chat {chat_id}: {e}")
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Sent text-only fallback message to Telegram chat {chat_id}.")
            return True
        except TelegramError as te:
            logger.error(f"Failed to send fallback message to Telegram chat {chat_id}: {te}")
            return False
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}.")
        try:
            await bot.send_message(chat_id=chat_id, text=f"{message}\n\n⚠️ Image file not found: {image_path}")
            return True
        except TelegramError as te:
            logger.error(f"Failed to send fallback message about missing image to Telegram chat {chat_id}: {te}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error while sending image to Telegram chat {chat_id}: {e}", exc_info=True)
        try:
            await bot.send_message(chat_id=chat_id, text=f"{message}\n\n⚠️ An unexpected error occurred.")
            return True
        except TelegramError as te:
            logger.error(f"Failed to send fallback message about unexpected error to Telegram chat {chat_id}: {te}")
            return False