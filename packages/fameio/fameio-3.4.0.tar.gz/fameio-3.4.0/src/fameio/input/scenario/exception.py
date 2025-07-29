# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any

from fameio.input import ScenarioError
from fameio.logs import log_error

_DEFAULT_USED = "Using default value '{}' for missing key '{}'"


def log_scenario_error(message: str) -> ScenarioError:
    """Creates exception with given `message`, logs it on level "Error" and returns it.

    Args:
        message: to be logged and included in the exception if key is missing

    Returns:
        created ScenarioError, logged on level "ERROR"
    """
    error = ScenarioError(message)
    log_error(error)
    return error


def get_or_raise(dictionary: dict, key: str, error_message: str) -> Any:
    """Returns value associated with `key` in given `dictionary`, or raises exception if key or value is missing.

    Args:
        dictionary: to search the key in
        key: to be searched
        error_message: to be logged and included in the raised exception if key is missing

    Returns:
        value associated with given key in given dictionary

     Raises:
         ScenarioError: if given key is not in given dictionary or value is None, logged on level "ERROR"
    """
    if key not in dictionary or dictionary[key] is None:
        raise log_scenario_error(error_message.format(key))
    return dictionary[key]


def assert_or_raise(assertion: bool, error_message: str) -> None:
    """Raises exception with given `error_message` if `assertion` is False.

    Args:
        assertion: expression that must be True, else an exception is raised
        error_message: to be logged and included in the raised exception if key is missing

    Raises:
        ScenarioError: if assertion is False, logged on level "ERROR"
    """
    if not assertion:
        raise log_scenario_error(error_message)
