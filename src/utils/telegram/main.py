# src/utils/telegram/main.py

import requests
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict
from src.config import settings
from src.logger import logger  # Import from logger_config to avoid circular imports

internal_logger = logger.getChild("telegram")

# Dictionary to store the last sent time for each sender
_last_sent_times: Dict[str, datetime] = {}
_lock = Lock()


def send_telegram_message(message: str, sender_id: str) -> bool:
    """
    Sends a message to a specified Telegram chat using a bot.
    Implements a 12-hour rate limit per sender to prevent duplicate notifications.

    Args:
        message (str): The message content to send.
        sender_id (str): A unique identifier for the message sender.

    Returns:
        bool: True if the message was sent successfully or silenced due to rate limiting,
              False if there was an error sending the message.
    """
    telegram_api_url = f"https://api.telegram.org/bot{settings.telegram.bot_token}/sendMessage"
    payload = {"chat_id": settings.telegram.chat_id, "text": message, "parse_mode": "Markdown"}
    current_time = datetime.now(timezone.utc)
    cooldown_period = timedelta(hours=12)

    with _lock:
        last_sent_time = _last_sent_times.get(sender_id)
        if last_sent_time:
            time_since_last_send = current_time - last_sent_time
            if time_since_last_send < cooldown_period:
                remaining_time = cooldown_period - time_since_last_send
                internal_logger.info(
                    f"Notification silenced for sender '{sender_id}'. "
                    f"Time remaining: {remaining_time}."
                )
                return True  # Silenced, not an error

        # Update the last sent time to current time
        _last_sent_times[sender_id] = current_time

    try:
        response = requests.post(telegram_api_url, data=payload)
        response.raise_for_status()
        internal_logger.info(f"Telegram message sent successfully for sender '{sender_id}'.")
        return True
    except requests.RequestException as e:
        internal_logger.error(f"Failed to send Telegram message for sender '{sender_id}': {e}")
        return False
