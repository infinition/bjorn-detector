#!/usr/bin/env python3
"""
control_commit/main.py

A script to validate commit messages and add appropriate icons based on commit types.
Ensures that commit messages follow a specific structure and naming conventions.
Adds icons to commit messages that do not contain square brackets [].
"""

import argparse
import logging
import re
import subprocess
import sys
from logging.handlers import RotatingFileHandler

# Mapping of commit types to icons
TYPE_MAPPING = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📝",
    "style": "💄",
    "refactor": "♻️",
    "perf": "⚡️",
    "test": "✅",
    "chore": "🔧",
}

# Regular expressions for detecting commit types and validating commit message structure
COMMIT_TYPE_REGEX = re.compile(r"^(?P<type>feat|fix|docs|style|refactor|perf|test|chore)")
COMMIT_MESSAGE_REGEX = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|chore)"
    r"(?:\((?P<scope>[a-z0-9\-]+)\))?:\s+"
    r"(?P<description>[a-z].+)$"
)

# Initialize the logger
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Validate commit messages and add icons based on commit types. "
            "Ensures commit messages follow the format: type(scope): description."
        )
    )
    parser.add_argument(
        "--log-level",
        choices=["INFO", "DEBUG"],
        default="INFO",
        help="Set the logging level. Default is INFO.",
    )
    return parser.parse_args()


def configure_logger(log_level: str) -> None:
    """
    Configures logging for the script.

    Args:
        log_level (str): Logging level as a string (e.g., 'INFO', 'DEBUG').
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logger.setLevel(numeric_level)

    # Set up log rotation: max size 5MB, keep 5 backup files
    file_handler = RotatingFileHandler(
        "commit_msg_icon_adder.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",  # Ensure UTF-8 encoding to handle emojis
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Create a safe console handler that replaces unencodable characters
    class SafeStreamHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                # Replace characters that can't be encoded
                msg = msg.encode(self.stream.encoding, errors="replace").decode(
                    self.stream.encoding
                )
                self.stream.write(msg + self.terminator)
                self.flush()
            except Exception as e_handle_emit:
                logger.debug(f"SafeStreamHandler error: {e_handle_emit}")
                self.handleError(record)

    safe_console_handler = SafeStreamHandler()
    safe_console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(safe_console_handler)


def read_commit_message(file_path: str) -> str:
    """
    Reads the commit message from the given file.

    Args:
        file_path (str): Path to the commit message file.

    Returns:
        str: The commit message.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            commit_msg = file.read().strip()
            logger.debug(f"Original commit message: {commit_msg}")
            return commit_msg
    except FileNotFoundError:
        logger.error(f"Commit message file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading commit message file: {e}")
        sys.exit(1)


def validate_commit_message(commit_msg: str) -> bool:
    """
    Validates the commit message against the required structure and lowercase naming.

    Args:
        commit_msg (str): The commit message to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    match = COMMIT_MESSAGE_REGEX.match(commit_msg)
    if match or commit_msg.__contains__("Bump version:"):
        logger.debug("Commit message structure is valid.")
        return True
    else:
        logger.error("Invalid commit message structure. Ensure it follows the format:")
        logger.error("type(scope): description")
        logger.error(" - type: feat, fix, docs, style, refactor, perf, test, chore (lowercase)")
        logger.error(" - scope: optional, lowercase, alphanumeric and hyphens")
        logger.error(" - description: starts with a lowercase letter")
        return False


def add_icon_to_commit_message(commit_type: str, existing_commit_msg: str) -> str:
    """
    Adds an icon to the commit message based on its type if it doesn't already have one.

    Args:
        commit_type (str): The type of the commit (e.g., 'chore', 'fix').
        existing_commit_msg (str): The original commit message.

    Returns:
        str: The commit message with the icon prepended.
    """
    icon = TYPE_MAPPING.get(commit_type.lower(), "")
    if icon and not existing_commit_msg.startswith(icon):
        new_commit_msg = f"{icon} {existing_commit_msg}"
        logger.debug(f"Updated commit message with icon: {new_commit_msg}")
        return new_commit_msg
    logger.debug("Icon already present in commit message or no icon defined for commit type.")
    return existing_commit_msg


def amend_commit(new_commit_msg: str) -> None:
    """
    Amends the current commit with the new commit message.

    Args:
        new_commit_msg (str): The new commit message.

    Raises:
        subprocess.CalledProcessError: If git amend fails.
    """
    try:
        # Amend the commit with the new commit message
        subprocess.run(["git", "commit", "--amend", "-m", new_commit_msg], check=True)
        logger.info("Successfully amended the commit with the new commit message.")
        logger.info(
            "Please perform a push using 'git push' to update the remote repository. Avoid use --force"
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to amend the commit: {e}")
        sys.exit(1)


def has_square_brackets(commit_msg: str) -> bool:
    """
    Checks if the commit message contains square brackets.

    Args:
        commit_msg (str): The commit message.

    Returns:
        bool: True if square brackets are present, False otherwise.
    """
    return bool(re.search(r"\[.*?\]", commit_msg))


def main() -> None:
    """
    Main function to validate commit messages and add icons if necessary.
    Exits with code 1 if validation fails or after adding an icon.
    """
    global commit_msg_without_icon
    args = parse_arguments()
    configure_logger(args.log_level)

    commit_msg_file = ".git/COMMIT_EDITMSG"
    commit_msg = read_commit_message(commit_msg_file)

    # Verify if the commit message already starts with an icon
    icon_present = False
    for icon in TYPE_MAPPING.values():
        if commit_msg.startswith(f"{icon} "):
            icon_present = True
            commit_msg_without_icon = commit_msg[len(icon) + 1 :]
            logger.debug(f"Commit message already has icon '{icon}'.")
            break

    if commit_msg.__contains__("Bump version:"):
        logger.debug("Commit message with icon is valid.")
        sys.exit(0)  # Valid commit message with icon; proceed
    elif icon_present:
        # Validate the commit message without the icon
        if not validate_commit_message(commit_msg_without_icon):
            logger.error("Commit message validation failed after removing icon. Aborting commit.")
            sys.exit(1)
        else:
            logger.debug("Commit message with icon is valid.")
            sys.exit(0)  # Valid commit message with icon; proceed
    else:
        # Validate the original commit message
        if not validate_commit_message(commit_msg):
            logger.error("Commit message validation failed. Aborting commit.")
            sys.exit(1)
        logger.debug("Commit message does not contain square brackets. Proceeding to add icon.")

        # Determine the type of commit to get the appropriate icon
        type_match = COMMIT_TYPE_REGEX.match(commit_msg)
        if type_match:
            commit_type = type_match.group("type")
            logger.debug(f"Detected commit type: {commit_type}")
        else:
            commit_type = "chore"  # Default to 'chore' if no type is found
            logger.debug("No commit type detected. Defaulting to 'chore'.")
            sys.exit(1)

        # Add the icon to the existing commit message
        updated_commit_msg = add_icon_to_commit_message(commit_type, commit_msg)

        # Write the updated commit message back to the file
        amend_commit(updated_commit_msg)

        # Inform the user and abort the commit to allow them to review the amended message
        logger.info(
            "Commit message has been updated with an icon. Please review and finalize the commit."
        )
        sys.exit(1)


if __name__ == "__main__":
    """"""
    main()
