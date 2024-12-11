# tests/test_main.py

import sys
import os
import pytest
import logging
from unittest import mock
from unittest.mock import patch, MagicMock
from argparse import Namespace
import socket

# Add the 'src' directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Now import the functions and classes from main.py
from src.main import (
    parse_arguments,
    configure_logger,
    notify_found,
    MainThread,
    MainWindow,
    OrbitIcon,
)


# Fixture to reset logger handlers before each test
@pytest.fixture(autouse=True)
def reset_logger_handlers():
    logger = logging.getLogger("__main__")
    logger.handlers = []
    yield
    logger.handlers = []


def test_parse_arguments_no_args():
    """
    Test parse_arguments with no command-line arguments.
    """
    test_args = ["bjorn-detector.py"]
    with patch.object(sys, "argv", test_args):
        args = parse_arguments()
        assert args.identity_file is None
        assert args.timeout is None
        assert args.gui is False  # Because action='store_false'
        assert args.log_level == "INFO"


def test_parse_arguments_all_args():
    """
    Test parse_arguments with all command-line arguments.
    """
    test_args = [
        "bjorn-detector.py",
        "--identity-file",
        "path/to/id_file",
        "--timeout",
        "120",
        "--no-gui",
        "--log-level",
        "DEBUG",
    ]
    with patch.object(sys, "argv", test_args):
        args = parse_arguments()
        assert args.identity_file == "path/to/id_file"
        assert args.timeout == 120
        assert args.gui is False  # --no-gui sets gui to False
        assert args.log_level == "DEBUG"


def test_parse_arguments_invalid_log_level():
    """
    Test parse_arguments with an invalid log level.
    """
    test_args = ["bjorn-detector.py", "--log-level", "INVALID"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            parse_arguments()


def test_configure_logger_info_level():
    """
    Test configure_logger with INFO level.
    """
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        configure_logger("INFO")

        mock_logger.setLevel.assert_called_with(logging.INFO)
        assert mock_logger.addHandler.call_count == 2  # File handler and console handler
        mock_logger.handlers.clear.assert_called_once()


def test_configure_logger_invalid_level():
    """
    Test configure_logger with an invalid logging level.
    """
    with pytest.raises(ValueError) as exc_info:
        configure_logger("INVALID_LEVEL")
    assert "Invalid log level: INVALID_LEVEL" in str(exc_info.value)


@patch("main.send_telegram_message")
@patch("main.send_discord_message")
@patch("main.send_smtp_email")
def test_notify_found_telegram(
    mock_send_smtp, mock_send_discord, mock_send_telegram, mock_settings
):
    """
    Test notify_found function when Telegram settings are available.
    """
    mock_settings.telegram_bot_token = "dummy_token"
    mock_settings.telegram_chat_id = "dummy_chat_id"
    mock_settings.discord_webhook_url = None
    mock_settings.smtp_server = None
    mock_settings.smtp_port = None

    bjorn_ip = "192.168.1.100"

    # Call notify_found
    notify_found(bjorn_ip)

    # Assert that send_telegram_message was called
    mock_send_telegram.assert_called_once_with(
        "🔍 *Bjorn Device Detected!* 🖥️\nIP Address: 192.168.1.100", "Bjorn Bot"
    )
    # Assert that other notification methods were not called
    mock_send_discord.assert_not_called()
    mock_send_smtp.assert_not_called()


@patch("main.send_telegram_message")
@patch("main.send_discord_message")
@patch("main.send_smtp_email")
def test_notify_found_discord(mock_send_smtp, mock_send_discord, mock_send_telegram, mock_settings):
    """
    Test notify_found function when Discord settings are available.
    """
    mock_settings.telegram_bot_token = None
    mock_settings.telegram_chat_id = None
    mock_settings.discord_webhook_url = "https://discord.com/api/webhooks/..."
    mock_settings.smtp_server = None
    mock_settings.smtp_port = None

    bjorn_ip = "192.168.1.100"

    # Call notify_found
    notify_found(bjorn_ip)

    # Assert that send_discord_message was called
    mock_send_discord.assert_called_once_with(
        "🔍 *Bjorn Device Detected!* 🖥️\nIP Address: 192.168.1.100", "no-reply@bjorn.bot"
    )
    # Assert that other notification methods were not called
    mock_send_telegram.assert_not_called()
    mock_send_smtp.assert_not_called()


@patch("main.send_telegram_message")
@patch("main.send_discord_message")
@patch("main.send_smtp_email")
def test_notify_found_smtp(mock_send_smtp, mock_send_discord, mock_send_telegram, mock_settings):
    """
    Test notify_found function when SMTP settings are available.
    """
    mock_settings.telegram_bot_token = None
    mock_settings.telegram_chat_id = None
    mock_settings.discord_webhook_url = None
    mock_settings.smtp_server = "smtp.example.com"
    mock_settings.smtp_port = 587

    bjorn_ip = "192.168.1.100"

    # Call notify_found
    notify_found(bjorn_ip)

    # Assert that send_smtp_email was called
    mock_send_smtp.assert_called_once_with(
        "Bjorn Device Detected",
        "🔍 *Bjorn Device Detected!* 🖥️\nIP Address: 192.168.1.100".replace("🔍 ", "").replace(
            "🖥️\n", "\n"
        ),
        "no-reply@bjorn.bot",
    )
    # Assert that other notification methods were not called
    mock_send_telegram.assert_not_called()
    mock_send_discord.assert_not_called()


@patch("main.logger")
@patch("socket.gethostbyname")
@patch("main.notify_found")
def test_main_thread_run_success(mock_notify_found, mock_gethostbyname, mock_logger):
    """
    Test MainThread.run when bjorn.home is reachable.
    """
    mock_gethostbyname.return_value = "192.168.1.100"

    main_thread = MainThread(timeout=10)
    main_thread.stop = MagicMock()

    with patch("time.sleep", return_value=None):
        with patch("time.time", side_effect=[0, 5, 15, 20]):
            with patch.object(main_thread, "_stop_event", MagicMock()):
                main_thread.run()

    # Assert that notify_found was called
    assert mock_notify_found.call_count >= 1
    # Assert that logger.info was called
    mock_logger.info.assert_any_call("Bjorn device is reachable. Bjorn device IP: 192.168.1.100")


@patch("main.logger")
@patch("socket.gethostbyname", side_effect=socket.gaierror)
@patch("main.notify_found")
def test_main_thread_run_failure(mock_notify_found, mock_gethostbyname, mock_logger):
    """
    Test MainThread.run when bjorn.home is not reachable.
    """
    main_thread = MainThread(timeout=10)
    main_thread.stop = MagicMock()

    with patch("time.sleep", return_value=None):
        with patch("time.time", side_effect=[0, 5, 15, 20]):
            with patch.object(main_thread, "_stop_event", MagicMock()):
                main_thread.run()

    # Assert that notify_found was called
    assert mock_notify_found.call_count >= 1
    # Assert that logger.warning was called
    mock_logger.warning.assert_any_call("Bjorn device is not reachable.")
    mock_logger.warning.assert_any_call("Timeout reached. No response after 10 seconds.")


@patch("main.logger")
@patch("socket.gethostbyname")
@patch("main.notify_found")
def test_notify_found_no_configuration(
    mock_notify_found, mock_gethostbyname, mock_logger, mock_settings
):
    """
    Test notify_found when no notification configurations are set.
    """
    mock_settings.telegram_bot_token = None
    mock_settings.telegram_chat_id = None
    mock_settings.discord_webhook_url = None
    mock_settings.smtp_server = None
    mock_settings.smtp_port = None

    bjorn_ip = "192.168.1.100"

    notify_found(bjorn_ip)

    # Assert that no notification functions were called
    mock_notify_found.assert_not_called()

    # Assert that logger.debug was called with "No notification configuration."
    mock_logger.debug.assert_called_once_with("No notification configuration.")


def test_main_no_gui_missing_files(tmp_path):
    """
    Test main function in non-GUI mode when required files are missing.
    """
    # Mock os.path.exists to return False for any file
    with patch("os.path.exists", return_value=False):
        with patch("main.logger") as mock_logger:
            from main import main

            with patch("sys.argv", ["bjorn-detector.py", "--no-gui"]):
                with pytest.raises(SystemExit):
                    main()
            # Assert that logger.error was called for missing files
            mock_logger.error.assert_any_call("File: src//static//images//icon.ico doesn't exist")
            # Depending on how main() handles multiple missing files, there could be multiple error logs
