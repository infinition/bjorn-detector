#!/usr/bin/env python3
"""
commit_msg_version_bump.py

A script to bump the version in pyproject.toml based on the latest commit message.
Changes the commit message to include the version bump and adds an icon.
Ensures that changes are committed in a single step.

Usage:
    commit_msg_version_bump.py [--log-level {INFO,DEBUG}]
"""

import argparse
import logging
import re
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

import toml

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

# Mapping of commit types to version bump parts
VERSION_BUMP_MAPPING = {
    "feat": "minor",
    "fix": "patch",
    "docs": "patch",
    "style": "patch",
    "refactor": "patch",
    "perf": "patch",
    "test": "patch",
    "chore": "patch",
}

# Regular expressions for detecting commit types and versioning keywords
COMMIT_TYPE_REGEX = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|chore)", re.IGNORECASE
)
VERSION_KEYWORD_REGEX = re.compile(
    r"\[(?P<keyword>major candidate|minor candidate|patch candidate)]$", re.IGNORECASE
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
            "Bump the version in pyproject.toml based on the latest commit message. "
            "Adds icons to commit messages depending on their type."
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
        "commit_msg_version.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_latest_commit_message() -> str:
    """
    Retrieves the latest commit message.

    Returns:
        str: The latest commit message.
    """
    try:
        message = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
        logger.debug(f"Latest commit message: {message}")
        return message
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving latest commit message: {e.stderr}")
        sys.exit(1)


def get_current_version(pyproject_path: str = "pyproject.toml") -> str:
    """
    Retrieves the current version from pyproject.toml.

    Args:
        pyproject_path (str): Path to the pyproject.toml file.

    Returns:
        str: The current version string.
    """
    try:
        with open(pyproject_path, "r", encoding="utf-8") as file:
            data = toml.load(file)
        version = data["tool"]["poetry"]["version"]
        logger.debug(f"Current version: {version}")
        return version
    except (FileNotFoundError, KeyError, ValueError, toml.TomlDecodeError) as e:
        logger.error(f"Error retrieving the version from {pyproject_path}: {e}")
        sys.exit(1)


def get_new_version(pyproject_path: str = "pyproject.toml") -> str:
    """
    Retrieves the new version from pyproject.toml after bump.

    Args:
        pyproject_path (str): Path to the pyproject.toml file.

    Returns:
        str: The new version string.
    """
    try:
        with open(pyproject_path, "r", encoding="utf-8") as file:
            data = toml.load(file)
        new_version = data["tool"]["poetry"]["version"]
        logger.debug(f"New version: {new_version}")
        return new_version
    except (FileNotFoundError, KeyError, ValueError, toml.TomlDecodeError) as e:
        logger.error(f"Error retrieving the new version from {pyproject_path}: {e}")
        sys.exit(1)


def add_icon_and_prepare_commit_message(current_version: str, new_version: str) -> str:
    """
    Prepares the new commit message with the icon and version bump.

    Args:
        current_version (str): The current version before bump.
        new_version (str): The new version after bump.

    Returns:
        str: The new commit message.
    """
    icon = "🔖"
    new_commit_msg = f"{icon} Bump version: {current_version} → {new_version}"
    logger.debug(f"New commit message: {new_commit_msg}")
    return new_commit_msg


def bump_version(part: str) -> None:
    """
    Bumps the specified part of the version using bump2version.

    Args:
        part (str): The part of the version to bump ('major', 'minor', 'patch').

    Raises:
        subprocess.CalledProcessError: If bump2version fails.
    """
    try:
        subprocess.run(
            ["bump2version", part],
            check=True,
            encoding="utf-8",
        )
        logger.info(f"Successfully bumped the {part} version.")
    except subprocess.CalledProcessError as error:
        logger.error(f"Failed to bump the {part} version: {error}")
        sys.exit(1)


def stage_changes(pyproject_path: str = "pyproject.toml") -> None:
    """
    Stages the specified file for commit.

    Args:
        pyproject_path (str): Path to the file to stage.
    """
    try:
        subprocess.run(
            ["git", "add", pyproject_path],
            check=True,
            encoding="utf-8",
        )
        logger.debug(f"Staged {pyproject_path} for commit.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stage {pyproject_path}: {e}")
        sys.exit(1)


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
        subprocess.run(
            ["git", "commit", "--amend", "-m", new_commit_msg],
            check=True,
            encoding="utf-8",
        )
        logger.info("Successfully amended the commit with the new version bump.")
        logger.info(
            "Please perform a push using 'git push' to update the remote repository. Avoid using --force"
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to amend the commit: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main function to parse the latest commit message, add an icon, perform version bumping, and amend the commit.
    """
    args = parse_arguments()
    configure_logger(args.log_level)

    latest_commit_msg = get_latest_commit_message()

    type_match = COMMIT_TYPE_REGEX.match(latest_commit_msg)
    if type_match:
        commit_type = type_match.group("type")
        logger.debug(f"Detected commit type: {commit_type}")
    else:
        logger.debug("No commit type detected. Defaulting to 'chore'.")

    version_bump_part = determine_version_bump(latest_commit_msg)

    if version_bump_part:
        logger.info(f"Version bump detected: {version_bump_part}")

        current_version = get_current_version()

        bump_version(version_bump_part)

        new_version = get_new_version()

        updated_commit_msg = add_icon_and_prepare_commit_message(current_version, new_version)

        # Stage the updated pyproject.toml
        stage_changes()

        amend_commit(updated_commit_msg)

        logger.info(
            "Aborting the current push. Please perform a push using 'git push'. Avoid using --force"
        )
        sys.exit(1)
    else:
        logger.info("No version bump detected in commit message.")


def determine_version_bump(commit_msg: str) -> Optional[str]:
    """
    Determines the version bump part based on the commit message.

    Args:
        commit_msg (str): The commit message.

    Returns:
        Optional[str]: The version part to bump ('major', 'minor', 'patch') or None.
    """
    logger.debug(f"Detected commit message: {commit_msg}")
    match = VERSION_KEYWORD_REGEX.search(commit_msg)
    if match:
        keyword = match.group("keyword").lower()
        if "major" in keyword:
            return "major"
        elif "minor" in keyword:
            return "minor"
        elif "patch" in keyword:
            return "patch"
    else:
        return None
    return None


if __name__ == "__main__":
    main()
