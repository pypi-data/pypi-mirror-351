# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path
from typing import Any

from fameio.logs import log_error

CSV_FILE_SUFFIX = ".csv"

_ERR_INVALID_PATTERN = "Pattern '{}' cannot be used here due to: '{}'"


def keys_to_lower(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Returns new dictionary content of given `dictionary` but its top-level `keys` in lower case."""
    return {keys.lower(): value for keys, value in dictionary.items()}


def ensure_is_list(value: Any) -> list:
    """Returns a list: Either the provided `value` if it is a list, or a new list containing the provided value."""
    if isinstance(value, list):
        return value
    return [value]


def ensure_path_exists(path: Path | str):
    """Creates a specified path if not already existent."""
    Path(path).mkdir(parents=True, exist_ok=True)


def clean_up_file_name(name: str) -> str:
    """Returns given `name` replacing spaces and colons with underscore, and slashed with a dash."""
    translation_table = str.maketrans({" ": "_", ":": "_", "/": "-"})
    return name.translate(translation_table)


def get_csv_files_with_pattern(base_path: Path, pattern: str) -> list[Path]:
    """Find all csv files matching the given `pattern` based on the given `base_path`.

    Args:
        base_path: to start the search from
        pattern: to match the files against that are to be found

    Returns:
        Full file paths for files ending with ".csv" and matching the given pattern

    Raises:
        ValueError: if pattern cannot be used to search path, logged with level "ERROR"
    """
    try:
        return [file for file in base_path.glob(pattern) if file.suffix.lower() == CSV_FILE_SUFFIX]
    except NotImplementedError as e:
        raise log_error(ValueError(_ERR_INVALID_PATTERN.format(pattern, e))) from e


def extend_file_name(original_file: Path, appendix: str) -> Path:
    """Return original file path, but appending `FILE_NAME_APPENDIX` before the suffix.

    Args:
        original_file: from which to derive the new path
        appendix: to be added to the end of the file name before the suffix

    Returns:
        new file path including the appendix in the file name
    """
    return Path(original_file.parent, original_file.stem + appendix + original_file.suffix)
