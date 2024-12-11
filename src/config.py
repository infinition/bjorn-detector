from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Global Configuration
    timeout: int = Field(50, env="TIMEOUT", description="Timeout in seconds")

    # Telegram
    telegram_bot_token: Optional[str] = Field(
        None, env="TELEGRAM_BOT_TOKEN", description="Telegram bot token"
    )
    telegram_chat_id: Optional[str] = Field(
        None, env="TELEGRAM_CHAT_ID", description="Telegram chat ID"
    )

    # Discord
    discord_webhook_url: Optional[str] = Field(
        None, env="DISCORD_WEBHOOK_URL", description="Discord webhook URL"
    )

    # SMTP
    smtp_server: Optional[str] = Field(None, env="SMTP_SERVER", description="SMTP server address")
    smtp_port: Optional[int] = Field(None, env="SMTP_PORT", description="SMTP server port")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME", description="SMTP username")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD", description="SMTP password")
    smtp_from_email: Optional[str] = Field(
        None, env="SMTP_FROM_EMAIL", description="Sender email address"
    )
    smtp_to_email: Optional[str] = Field(
        None, env="SMTP_TO_EMAIL", description="Recipient email address"
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
