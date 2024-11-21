#!/usr/bin/env python3
"""
bump_year.py

A script to bump the year part of the version in pyproject.toml.
Resets major and minor versions to 0 when the year is incremented.
Additionally, updates the footers of specified Markdown files that contain the year.

Usage:
    python bump_year.py
    python bump_year.py --md-files README.md CONTRIBUTING.md
    python bump_year.py --md-dir docs/
"""

import argparse
import logging
import datetime
import os
import re
from typing import List
from logging.handlers import RotatingFileHandler

# Initialize the logger
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Update Markdown footers containing the year.")
    parser.add_argument(
        "--md-files",
        nargs="*",
        default=[
            "README.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "VERSIONING.md",
            "LICENSE",
        ],
        help="List of Markdown files to update footers. Example: --md-files README.md CONTRIBUTING.md",
    )
    parser.add_argument(
        "--md-dir",
        type=str,
        default=None,
        help="Directory containing Markdown files to update footers. Example: --md-dir docs/",
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
    file_handler = RotatingFileHandler("bump_year.log", maxBytes=5 * 1024 * 1024, backupCount=5)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def update_markdown_footers(md_files: List[str], current_year: int) -> None:
    """
    Updates the footer year in specified Markdown files.

    Args:
        md_files (List[str]): List of Markdown file paths.
        current_year (int): The current year.
    """
    year_pattern = re.compile(r"(\b20\d{2}\b)")  # Matches years from 2000 to 2099

    for md_file in md_files:
        if not os.path.isfile(md_file):
            logger.warning(f"{md_file} does not exist. Skipping.")
            continue

        try:
            with open(md_file, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            logger.error(f"Error reading {md_file}: {e}")
            continue

        logger.debug(f"Current year: {current_year}")

        # Find all years in the content
        years_found = year_pattern.findall(content)
        if not years_found:
            logger.debug(f"No years found in {md_file}. Skipping.")
            continue

        for year in years_found:
            logger.debug(f"Updating footer for year: {year} in {md_file}")
            if int(year) == int(current_year):
                logger.debug(f"No years to update found in {md_file}. Skipping.")
                continue

        # Replace the last occurrence of a year in the footer
        # Assumption: The footer is at the end of the file
        lines = content.strip().split("\n")
        footer_updated = False

        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            if year_pattern.search(line) and line.__contains__(str(int(current_year) - 1)):
                new_line = year_pattern.sub(str(current_year), line, count=1)
                lines[i] = new_line
                footer_updated = True
                logger.info(f"Updated year in {md_file}: '{line}' -> '{new_line}'")
                break

        if footer_updated:
            new_content = "\n".join(lines) + "\n"
            try:
                with open(md_file, "w", encoding="utf-8") as file:
                    file.write(new_content)
                logger.info(f"Successfully updated {md_file}.")
            except Exception as e:
                logger.error(f"Error writing to {md_file}: {e}")
        else:
            logger.warning(f"No footer with a year to update found in {md_file}. Skipping.")


def collect_markdown_files(md_files: List[str], md_dir: str = None) -> List[str]:
    """
    Collects Markdown files from specified files and/or directory.

    Args:
        md_files (List[str]): List of Markdown file paths.
        md_dir (str, optional): Directory to search for Markdown files.

    Returns:
        List[str]: Combined list of Markdown file paths.
    """
    collected_files = set(md_files)

    if md_dir:
        if not os.path.isdir(md_dir):
            logger.warning(f"Directory {md_dir} does not exist. Skipping.")
        else:
            for root, _, files in os.walk(md_dir):
                for file in files:
                    if file.lower().endswith(".md"):
                        collected_files.add(os.path.join(root, file))

    return list(collected_files)


def main() -> None:
    """
    Main function to execute the year bumping and Markdown footers updating process.
    """
    current_year = datetime.datetime.now().year

    # Collect Markdown files to update
    markdown_files = collect_markdown_files(args.md_files, args.md_dir)

    if markdown_files:
        update_markdown_footers(markdown_files, current_year)
    else:
        logger.error("No Markdown files specified for footer update.")


if __name__ == "__main__":
    args = parse_arguments()
    configure_logger(args.log_level)
    main()
