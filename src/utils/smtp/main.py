# src/utils/smtp/main.py

import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict
from src.config import settings
from src.logger import logger  # Import from logger_config to avoid circular imports

internal_logger = logger.getChild("smtp")

# Dictionary to store the last sent time for each sender
_last_sent_times: Dict[str, datetime] = {}
_lock = Lock()


def send_smtp_email(subject: str, body: str, sender_id: str) -> bool:
    """
    Sends an email using SMTP with a 12-hour rate limit per sender to prevent duplicate notifications.

    Args:
        subject (str): Subject of the email.
        body (str): Body of the email.
        sender_id (str): A unique identifier for the message sender.

    Returns:
        bool: True if the email was sent successfully or silenced due to rate limiting,
              False if there was an error sending the email.
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp.from_email
    msg["To"] = settings.smtp.to_email

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
        with smtplib.SMTP(settings.smtp.smtp_server, settings.smtp.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp.username, settings.smtp.password)
            server.send_message(msg)
        internal_logger.info(f"SMTP email sent successfully for sender '{sender_id}'.")
        return True
    except Exception as e:
        internal_logger.error(f"Failed to send SMTP email for sender '{sender_id}': {e}")
        return False
