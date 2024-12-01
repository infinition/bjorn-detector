# src/utils/discord/main.py

import requests
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict
from src.config import settings
from src.logger import logger  # Import from logger_config to avoid circular imports

internal_logger = logger.getChild("discord")

# Dictionary to store the last sent time for each sender
_last_sent_times: Dict[str, datetime] = {}
_lock = Lock()


def send_discord_message(message: str, sender_id: str) -> bool:
    """
    Sends a message to a specified Discord channel using a webhook.
    If a message has already been sent by the same sender within the last 12 hours,
    the notification is silenced to prevent duplicate messages.

    Args:
        message (str): The message content to send.
        sender_id (str): A unique identifier for the message sender.

    Returns:
        bool: True if the message was sent successfully or silenced due to rate limiting,
              False if there was an error sending the message.
    """
    webhook_url = settings.discord_webhook_url
    payload = {"content": message}
    current_time = datetime.now(timezone.utc)
    cooldown_period = timedelta(hours=12)

    with _lock:
        last_sent_time = _last_sent_times.get(sender_id)
        if last_sent_time:
            time_since_last_send = current_time - last_sent_time
            if time_since_last_send < cooldown_period:
                remaining_time = cooldown_period - time_since_last_send
                internal_logger.info(
                    f"Notification silenced from sender '{sender_id}'. "
                    f"Time remaining: {remaining_time}."
                )
                return True  # Silenced, not an error

        # Update the last sent time to current time
        _last_sent_times[sender_id] = current_time

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        internal_logger.info(f"Discord message sent successfully from sender '{sender_id}'.")
        return True
    except requests.RequestException as e:
        internal_logger.error(f"Failed to send Discord message from sender '{sender_id}': {e}")
        return False
