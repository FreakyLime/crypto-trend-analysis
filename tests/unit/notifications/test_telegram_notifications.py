import pytest
from unittest.mock import AsyncMock, patch, mock_open
from notifications.telegram_notifications import send_analysis_to_telegram_with_image
from telegram.error import TelegramError

@pytest.mark.asyncio
@patch("notifications.telegram_notifications.Bot")
@patch("builtins.open", new_callable=mock_open, read_data="fake_image_data")
async def test_send_analysis_to_telegram_with_image_success(mock_open_file, mock_bot_class):
    mock_bot = AsyncMock()
    mock_bot_class.return_value = mock_bot

    result = await send_analysis_to_telegram_with_image(
        bot_token="test_token",
        chat_id="test_chat_id",
        message="Test message",
        image_path="test_image.jpg"
    )

    mock_bot.send_photo.assert_called_once_with(chat_id="test_chat_id", photo=mock_open_file(), caption="Test message")
    assert result is True

@pytest.mark.asyncio
@patch("notifications.telegram_notifications.Bot")
@patch("builtins.open", new_callable=mock_open, read_data="fake_image_data")
async def test_send_analysis_to_telegram_with_image_fallback_to_message(mock_open_file, mock_bot_class):
    mock_bot = AsyncMock()
    mock_bot.send_photo.side_effect = TelegramError("Failed to send photo")
    mock_bot_class.return_value = mock_bot

    result = await send_analysis_to_telegram_with_image(
        bot_token="test_token",
        chat_id="test_chat_id",
        message="Test message",
        image_path="test_image.jpg"
    )

    mock_bot.send_photo.assert_called_once_with(chat_id="test_chat_id", photo=mock_open_file(), caption="Test message")
    mock_bot.send_message.assert_called_once_with(chat_id="test_chat_id", text="Test message")
    assert result is True

@pytest.mark.asyncio
@patch("notifications.telegram_notifications.Bot")
async def test_send_analysis_to_telegram_with_image_file_not_found(mock_bot_class):
    mock_bot = AsyncMock()
    mock_bot_class.return_value = mock_bot

    result = await send_analysis_to_telegram_with_image(
        bot_token="test_token",
        chat_id="test_chat_id",
        message="Test message",
        image_path="missing_image.jpg"
    )

    mock_bot.send_message.assert_called_once_with(
        chat_id="test_chat_id",
        text="Test message\n\n⚠️ Image file not found: missing_image.jpg"
    )
    assert result is True

@pytest.mark.asyncio
@patch("notifications.telegram_notifications.Bot")
@patch("builtins.open", new_callable=mock_open, read_data="fake_image_data")
async def test_send_analysis_to_telegram_with_image_unexpected_error(mock_open_file, mock_bot_class):
    mock_bot = AsyncMock()
    mock_bot.send_photo.side_effect = Exception("Unexpected error")
    mock_bot_class.return_value = mock_bot

    result = await send_analysis_to_telegram_with_image(
        bot_token="test_token",
        chat_id="test_chat_id",
        message="Test message",
        image_path="test_image.jpg"
    )

    mock_bot.send_message.assert_called_once_with(
        chat_id="test_chat_id",
        text="Test message\n\n⚠️ An unexpected error occurred."
    )
    assert result is True