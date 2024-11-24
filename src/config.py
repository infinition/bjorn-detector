from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class TelegramSettings(BaseSettings):
    """
    Configurations for Telegram notifications.
    """

    bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN", description="Telegram bot token")
    chat_id: str = Field(..., env="TELEGRAM_CHAT_ID", description="Telegram chat ID")

    class Config:
        env_prefix = "TELEGRAM_"
        env_file = ".env"


class DiscordSettings(BaseSettings):
    """
    Configurations for Discord notifications.
    """

    webhook_url: str = Field(..., env="DISCORD_WEBHOOK_URL", description="Discord webhook URL")

    class Config:
        env_prefix = "DISCORD_"
        env_file = ".env"


class SMTPSettings(BaseSettings):
    """
    Configurations for SMTP (email) notifications.
    All fields are optional.
    """

    smtp_server: Optional[str] = Field(None, env="SMTP_SERVER", description="SMTP server address")
    smtp_port: Optional[int] = Field(None, env="SMTP_PORT", description="SMTP server port")
    username: Optional[str] = Field(None, env="SMTP_USERNAME", description="SMTP username")
    password: Optional[str] = Field(None, env="SMTP_PASSWORD", description="SMTP password")
    from_email: Optional[str] = Field(
        None, env="SMTP_FROM_EMAIL", description="Sender email address"
    )
    to_email: Optional[str] = Field(
        None, env="SMTP_TO_EMAIL", description="Recipient email address"
    )

    class Config:
        env_prefix = "SMTP_"
        env_file = ".env"


class Settings(BaseSettings):
    """
    General configurations including optional notification settings.
    """

    telegram: Optional[TelegramSettings] = None
    discord: Optional[DiscordSettings] = None
    smtp: Optional[SMTPSettings] = None
    timeout: int = Field(50, env="TIMEOUT", description="Timeout in seconds")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instantiate the settings
settings = Settings()
