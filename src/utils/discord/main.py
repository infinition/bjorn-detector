import logging
import requests
from src.config import settings
from typing import Optional


def send_discord_message(message: str) -> bool:
    """
    Sends a message to a specified Discord channel using a webhook.

    Args:
        message (str): The message to send.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    webhook_url = settings.discord.webhook_url
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logging.info("Discord message sent successfully.")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to send Discord message: {e}")
        return False
