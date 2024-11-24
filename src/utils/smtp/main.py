import logging
import smtplib
from email.mime.text import MIMEText
from src.config import settings
from typing import Optional


def send_smtp_email(subject: str, body: str) -> bool:
    """
    Sends an email using SMTP.

    Args:
        subject (str): Subject of the email.
        body (str): Body of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp.from_email
    msg["To"] = settings.smtp.to_email

    try:
        with smtplib.SMTP(settings.smtp.smtp_server, settings.smtp.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp.username, settings.smtp.password)
            server.send_message(msg)
        logging.info("SMTP email sent successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to send SMTP email: {e}")
        return False
