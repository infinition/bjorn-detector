import logging
import requests
from src.config import settings
from typing import Optional


def send_telegram_message(message: str) -> bool:
    """
    Sends a message to a specified Telegram chat using a bot.

    Args:
        message (str): The message to send.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    telegram_api_url = f"https://api.telegram.org/bot{settings.telegram.bot_token}/sendMessage"
    payload = {"chat_id": settings.telegram.chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(telegram_api_url, data=payload)
        response.raise_for_status()
        logging.info("Telegram message sent successfully.")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False
