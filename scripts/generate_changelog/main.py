#!/usr/bin/env python3
"""
generate_changelog.py

This script automatically generates or updates the CHANGELOG.md file based on commit messages.
It processes commit history, even if no Git tags exist, categorizes commits into sections like Features,
Bug Fixes, etc., and compiles them into a structured changelog.

Usage:
    python generate_changelog.py
    python generate_changelog.py --log-level DEBUG
"""

import argparse
import logging
import re
import subprocess
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Tuple
from collections import OrderedDict
import os
import sys

# Define the path to the CHANGELOG.md
CHANGELOG_PATH = "CHANGELOG.md"

# Define the commit message regex pattern
# Example: feat(authentication): add OAuth2 support [minor candidate]
COMMIT_REGEX = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|chore)"
    r"(?:\((?P<scope>[^)]+)\))?:\s+(?P<description>.+?)"
    r"\s+\[(?P<versioning_keyword>minor candidate|major candidate|patch candidate)]$",
    re.IGNORECASE,
)

# Mapping of commit types to changelog sections
TYPE_MAPPING = {
    "feat": "### Features",
    "fix": "### Bug Fixes",
    "docs": "### Documentation",
    "style": "### Styles",
    "refactor": "### Refactors",
    "perf": "### Performance Improvements",
    "test": "### Tests",
    "chore": "### Chores",
}

# Initialize the logger
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Automatically generate or update CHANGELOG.md based on commit messages."
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
        "changelog_sync.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def fetch_tags() -> None:
    """
    Fetches all tags from the remote repository to ensure the latest tags are available locally.
    """
    try:
        logger.debug("Fetching all Git tags from remote repository.")
        subprocess.check_output(["git", "fetch", "--tags"])
        logger.info("Successfully fetched Git tags.")
    except subprocess.CalledProcessError as error:
        logger.error(f"Error fetching Git tags: {error}")
        raise


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parses a version string into its major, minor, and patch components.

    Args:
        version_str (str): The version string (e.g., 'v1.0.8').

    Returns:
        Tuple[int, int, int]: A tuple containing major, minor, and patch numbers.
    """
    try:
        # Remove the 'v' prefix if present
        if version_str.startswith("v"):
            version_str = version_str[1:]
        # Remove any suffix after '-', e.g., '1.0.8-test' -> '1.0.8'
        version_str = version_str.split("-")[0]
        # Split into major, minor, patch and convert to integers
        major, minor, patch = map(int, version_str.split("."))
        return major, minor, patch
    except (ValueError, IndexError):
        logger.error(f"Invalid version format: {version_str}")
        return 0, 0, 0


def get_sorted_tags() -> List[str]:
    """
    Retrieves all semantic Git tags and sorts them in ascending order.

    Returns:
        List[str]: A list of sorted semantic Git tags.
    """
    version_pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
    try:
        logger.debug("Retrieving all Git tags.")
        tags = subprocess.check_output(["git", "tag", "--list"], encoding="utf-8").split("\n")
        tags = [tag.strip() for tag in tags if tag.strip()]
        semantic_tags = [tag for tag in tags if version_pattern.match(tag)]
        if not semantic_tags:
            logger.warning("No semantic Git tags found. Starting from scratch.")
            return []
        # Sort tags using semantic versioning in ascending order
        sorted_tags = sorted(
            semantic_tags, key=lambda s: parse_version(s), reverse=False  # Ascending order
        )
        logger.debug(f"Sorted semantic tags: {sorted_tags}")
        return sorted_tags
    except subprocess.CalledProcessError as error:
        logger.error(f"Error retrieving Git tags: {error}")
        return []


def get_all_commits(tags: List[str]) -> Dict[str, List[str]]:
    """
    Retrieves all commits and organizes them in an OrderedDict.

    Args:
        tags (List[str]): A list of sorted Git tags (ascending order).

    Returns:
        Dict[str, List[str]]: An OrderedDict where keys are versions (tags or 'Unreleased') and values are lists of commit messages.
    """
    commits_dict = OrderedDict()

    if not tags:
        # No tags exist, retrieve all commits
        try:
            logger.debug("No tags found. Retrieving all commits.")
            commits = subprocess.check_output(
                ["git", "log", "--pretty=format:%s", "--reverse"], encoding="utf-8"
            ).split("\n")
            commits = [commit.strip() for commit in commits if commit.strip()]
            if commits:
                commits_dict["Unreleased"] = commits
                logger.info(f"Number of commits retrieved: {len(commits)}")
        except subprocess.CalledProcessError as error:
            logger.error(f"Error retrieving all commits: {error}")
    else:
        # Process sorted_tags in ascending order
        previous_tag = None
        for tag in tags:
            if previous_tag:
                commit_range = f"{previous_tag}..{tag}"
            else:
                # From the beginning up to the first tag
                commit_range = tag
            try:
                logger.debug(f"Retrieving commits between {previous_tag} and {tag}.")
                commits = subprocess.check_output(
                    ["git", "log", commit_range, "--pretty=format:%s", "--reverse"],
                    encoding="utf-8",
                ).split("\n")
                commits = [commit.strip() for commit in commits if commit.strip()]
                if commits:
                    commits_dict[tag.lstrip("v")] = commits
                previous_tag = tag
            except subprocess.CalledProcessError as error:
                logger.error(f"Error retrieving commits between {previous_tag} and {tag}: {error}")

        # Handle commits after the latest tag (Unreleased)
        latest_tag = tags[-1]
        try:
            commit_range = f"{latest_tag}..HEAD"
            logger.debug(f"Retrieving commits after the latest tag: {latest_tag}")
            unreleased_commits = subprocess.check_output(
                ["git", "log", commit_range, "--pretty=format:%s", "--reverse"], encoding="utf-8"
            ).split("\n")
            unreleased_commits = [commit.strip() for commit in unreleased_commits if commit.strip()]
            if unreleased_commits:
                commits_dict["Unreleased"] = unreleased_commits
                logger.info(f"Number of unreleased commits: {len(unreleased_commits)}")
        except subprocess.CalledProcessError as error:
            logger.error(f"Error retrieving unreleased commits: {error}")

    return commits_dict


def parse_commits(commits: List[str]) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Parses commit messages and categorizes them based on type.

    Args:
        commits (List[str]): A list of commit messages.

    Returns:
        Tuple[Dict[str, List[str]], List[str]]: A dictionary categorizing commits and a list of non-conforming commits.
    """
    changelog: Dict[str, List[str]] = {section: [] for section in TYPE_MAPPING.values()}
    non_conforming_commits: List[str] = []

    for commit in commits:
        match = COMMIT_REGEX.match(commit)
        if match:
            commit_type = match.group("type").lower()
            scope = match.group("scope")
            description = match.group("description").strip()
            versioning_keyword = match.group("versioning_keyword").lower()

            section = TYPE_MAPPING.get(commit_type)
            if section:
                if scope:
                    entry = f"- **{scope}**: {description} ({versioning_keyword})"
                else:
                    entry = f"- {description} ({versioning_keyword})"
                changelog[section].append(entry)
                logger.debug(f"Commit categorized under {section}: {entry}")
            else:
                non_conforming_commits.append(commit)
                logger.debug(f"Commit type '{commit_type}' not recognized.")
        else:
            non_conforming_commits.append(commit)
            logger.debug(f"Commit does not match pattern: {commit}")

    # Remove empty sections
    changelog = {k: v for k, v in changelog.items() if v}
    logger.debug(f"Changelog categories: {list(changelog.keys())}")
    logger.debug(f"Non-conforming commits count: {len(non_conforming_commits)}")
    return changelog, non_conforming_commits


def generate_changelog_entry(
    version: str, changelog: Dict[str, List[str]], non_conforming: List[str]
) -> str:
    """
    Generates a changelog entry for a specific version.

    Args:
        version (str): The version number.
        changelog (Dict[str, List[str]]): The categorized changelog entries.
        non_conforming (List[str]): List of non-conforming commit messages.

    Returns:
        str: The formatted changelog entry.
    """
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = f"## [{version}] - {date}\n\n"
    logger.debug(f"Generating changelog entry for version {version}.")

    for section, items in changelog.items():
        entry += f"{section}\n"
        for item in items:
            entry += f"{item}\n"
        entry += "\n"

    if non_conforming:
        entry += "### Other Changes\n"
        for commit in non_conforming:
            entry += f"- {commit}\n"
        entry += "\n"

    logger.debug("Changelog entry generated.")
    return entry


def generate_full_changelog(commits_dict: Dict[str, List[str]]) -> str:
    """
    Generates the full changelog content from the commits' dictionary.

    Args:
        commits_dict (Dict[str, List[str]]): An OrderedDict with version keys and commit lists.

    Returns:
        str: The full formatted changelog content.
    """
    changelog_content = ""

    # Iterate over commits_dict in order to have the oldest versions first
    for version, commits in commits_dict.items():
        if not commits:
            continue
        changelog, non_conforming = parse_commits(commits)
        changelog_entry = generate_changelog_entry(version, changelog, non_conforming)
        changelog_content += changelog_entry

    return changelog_content


def update_changelog(new_content: str) -> bool:
    """
    Creates or updates the CHANGELOG.md file.

    Args:
        new_content (str): The new changelog content to write.

    Returns:
        bool: True if the changelog was updated, False if no changes were necessary.
    """
    logger.info(f"Checking if {CHANGELOG_PATH} needs to be updated.")
    try:
        if os.path.exists(CHANGELOG_PATH):
            with open(CHANGELOG_PATH, "r", encoding="utf-8") as file:
                existing_content = file.read()
        else:
            existing_content = ""
            logger.warning(f"{CHANGELOG_PATH} not found. A new changelog will be created.")
    except Exception as error:
        logger.error(f"Error reading {CHANGELOG_PATH}: {error}")
        return False

    # Compare the new content with the existing content
    if new_content.strip() == existing_content.strip():
        logger.info("No changes detected in the changelog. No update needed.")
        return False

    # Update the changelog
    try:
        with open(CHANGELOG_PATH, "w", encoding="utf-8") as file:
            file.write(new_content)
        logger.info(f"{CHANGELOG_PATH} has been updated.")
        return True
    except Exception as error:
        logger.error(f"Error updating {CHANGELOG_PATH}: {error}")
        return False


def main() -> None:
    """
    Main function to generate or update the CHANGELOG.md.
    """
    fetch_tags()
    sorted_tags = get_sorted_tags()
    commits_dict = get_all_commits(sorted_tags)
    changelog_content = generate_full_changelog(commits_dict)

    if not changelog_content:
        logger.info("No commits found to include in the changelog.")
        return

    # Check and update the changelog only if necessary
    updated = update_changelog(changelog_content)
    if not updated:
        logger.info("Changelog was not updated as there are no new changes.")


if __name__ == "__main__":
    args = parse_arguments()
    configure_logger(args.log_level)
    try:
        main()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
