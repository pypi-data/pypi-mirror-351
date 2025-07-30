import re
import logging
from typing import Iterator


def normalize_string(input_string: str, lower=True) -> str:
    """Normalize a string by converting it to lowercase, removing special characters, and trimming leading"""
    result = input_string

    if not lower:
        result = input_string.lower()

    # Remove characters that are not letters, digits, spaces, or underscores
    result = re.sub(r"[^\w\s]|_", "", result)

    # Replace multiple consecutive spaces with a single space
    result = re.sub(r"\s+", " ", result)

    # Trim leading and trailing spaces
    normalized_string = result.strip()

    return normalized_string


def read_lines(file_path: str) -> Iterator[str]:
    """Yield lines from a text file, stripping trailing newlines and leading/trailing whitespace."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                # Strip whitespace and newline characters from the beginning and end of the line
                clean_line = line.strip()
                if clean_line:  # This checks if the line is not empty after stripping
                    yield clean_line
    except FileNotFoundError:
        logging.error(f"Unable to find the file at the specified path: {file_path}")
        raise
    except IOError as e:
        logging.error(f"Error encountered while reading the file at {file_path}: {e}")
        raise
