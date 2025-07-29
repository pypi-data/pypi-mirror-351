# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import datetime as dt
import math
import re
from enum import Enum, auto
from typing import Any

from fameio.input import InputError
from fameio.logs import log_error
from fameio.output import OutputError

START_IN_REAL_TIME = "2000-01-01_00:00:00"
DATE_FORMAT = "%Y-%m-%d_%H:%M:%S"
DATE_REGEX = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}:[0-9]{2}:[0-9]{2}")
FAME_FIRST_DATETIME = dt.datetime.strptime(START_IN_REAL_TIME, DATE_FORMAT)
TIME_SPAN_REGEX = re.compile(r"^[0-9]+\s*[A-z]+$")


class ConversionError(InputError, OutputError):
    """Indicates that time stamp conversion failed."""


class TimeUnit(Enum):
    """Time units defined in FAME."""

    SECONDS = auto()
    MINUTES = auto()
    HOURS = auto()
    DAYS = auto()
    WEEKS = auto()
    MONTHS = auto()
    YEARS = auto()


class Constants:
    """Time steps in FAME simulations associated with corresponding TimeUnits."""

    FIRST_YEAR = 2000
    STEPS_PER_SECOND = 1
    SECONDS_PER_MINUTE = 60
    MINUTES_PER_HOUR = 60
    HOURS_PER_DAY = 24
    DAYS_PER_YEAR = 365
    STEPS_PER_MINUTE = STEPS_PER_SECOND * SECONDS_PER_MINUTE
    STEPS_PER_HOUR = STEPS_PER_MINUTE * MINUTES_PER_HOUR
    STEPS_PER_DAY = STEPS_PER_HOUR * HOURS_PER_DAY
    STEPS_PER_YEAR = STEPS_PER_DAY * DAYS_PER_YEAR
    STEPS_PER_WEEK = STEPS_PER_DAY * 7
    STEPS_PER_MONTH = int(STEPS_PER_YEAR / 12)

    steps_per_unit: dict[TimeUnit, int] = {
        TimeUnit.SECONDS: STEPS_PER_SECOND,
        TimeUnit.MINUTES: STEPS_PER_MINUTE,
        TimeUnit.HOURS: STEPS_PER_HOUR,
        TimeUnit.DAYS: STEPS_PER_DAY,
        TimeUnit.WEEKS: STEPS_PER_WEEK,
        TimeUnit.MONTHS: STEPS_PER_MONTH,
        TimeUnit.YEARS: STEPS_PER_YEAR,
    }


class FameTime:
    """Handles conversion of TimeSteps and TimeDurations into TimeStamps and vice versa."""

    _TIME_UNIT_UNKNOWN = "TimeUnit conversion of '{}' not implemented."
    _FORMAT_INVALID = "'{}' is not recognised as time stamp string - check its format."
    _INVALID_TIMESTAMP = "Cannot convert time stamp string '{}' - check its format."
    _INVALID_TOO_LARGE = "Cannot convert time stamp string '{}' - last day of leap year is Dec 30th!"
    _NO_TIMESTAMP = "Time value expected, but '{}' is neither a time stamp string nor an integer."
    _INVALID_DATE_FORMAT = "Received invalid date format '{}'."
    _INVALID_SPAN_FORMAT = "Time span must be provided in the format '<positive integer> <TimeUnit>' but was: '{}'"
    _INVALID_TIME_UNIT = f"Time span unit '{{}}' unknown, must be one of: {[u.name for u in TimeUnit]}"

    @staticmethod
    def convert_datetime_to_fame_time_step(datetime_string: str) -> int:
        """Converts Datetime string to FAME time step.

        Args:
            datetime_string: a datetime in FAME formatting

        Returns:
            corresponding FAME time step

        Raises:
            ConversionError: if string could not be interpreted or does not represent a valid FAME time step,
                logged with level "ERROR"
        """
        if not FameTime.is_datetime(datetime_string):
            raise log_error(ConversionError(FameTime._FORMAT_INVALID.format(datetime_string)))
        datetime = FameTime._convert_to_datetime(datetime_string)
        years_since_start_time = datetime.year - FAME_FIRST_DATETIME.year
        beginning_of_year = dt.datetime(year=datetime.year, month=1, day=1, hour=0, minute=0, second=0)
        seconds_since_beginning_of_year = int((datetime - beginning_of_year).total_seconds())
        steps_since_beginning_of_year = seconds_since_beginning_of_year * Constants.STEPS_PER_SECOND
        if steps_since_beginning_of_year > Constants.STEPS_PER_YEAR:
            raise log_error(ConversionError(FameTime._INVALID_TOO_LARGE.format(datetime_string)))
        year_offset = years_since_start_time * Constants.STEPS_PER_YEAR
        return year_offset + steps_since_beginning_of_year

    @staticmethod
    def _convert_to_datetime(datetime_string: str) -> dt.datetime:
        """Converts given `datetime_string` in FAME formatting to real-world datetime.

        Args:
            datetime_string: to be converted to datetime

        Returns:
            datetime representation of provided string

        Raises:
            ConversionError: if provided string could not be converted, logged with level "ERROR"
        """
        try:
            return dt.datetime.strptime(datetime_string, DATE_FORMAT)
        except ValueError as e:
            raise log_error(ConversionError(FameTime._INVALID_TIMESTAMP.format(datetime_string))) from e

    @staticmethod
    def convert_fame_time_step_to_datetime(fame_time_steps: int, date_format: str = DATE_FORMAT) -> str:
        """Converts given `fame_time_steps` to corresponding real-world datetime string in `date_format`.

        Args:
            fame_time_steps: an integer representing time in FAME's internal format
            date_format: to be used for datetime representation

        Returns:
            string representing the real-world datetime of the provided time steps

        Raises:
            ConversionError: if `date_format` is invalid, logged with level "ERROR"
        """
        years_since_start_time = math.floor(fame_time_steps / Constants.STEPS_PER_YEAR)
        current_year = years_since_start_time + Constants.FIRST_YEAR
        beginning_of_year = dt.datetime(year=current_year, month=1, day=1, hour=0, minute=0, second=0)
        steps_in_current_year = fame_time_steps - years_since_start_time * Constants.STEPS_PER_YEAR
        seconds_in_current_year = steps_in_current_year / Constants.STEPS_PER_SECOND
        datetime = beginning_of_year + dt.timedelta(seconds=seconds_in_current_year)
        try:
            return datetime.strftime(date_format)
        except ValueError as e:
            raise log_error(ConversionError(FameTime._INVALID_DATE_FORMAT.format(date_format))) from e

    @staticmethod
    def convert_time_span_to_fame_time_steps(value: int, unit: TimeUnit) -> int:
        """Converts value of `TimeUnit.UNIT` to FAME time steps.

        Args:
            value: amount of the units to be converted
            unit: base time unit

        Returns:
            FAME time steps equivalent of `value x unit`

        Raises:
            ConversionError: if an unknown time unit is used, logged with level "ERROR"
        """
        steps = Constants.steps_per_unit.get(unit)
        if steps:
            return steps * value
        raise log_error(ConversionError(FameTime._TIME_UNIT_UNKNOWN.format(unit)))

    @staticmethod
    def convert_text_to_time_span(string: str) -> int:
        """Converts given string in form of "<positive integer> <TimeUnit>" to a time span in FAME time steps.

        Args:
            string: to convert to a time span from

        Returns:
            FAME time steps equivalent of `value x unit`

        Raises:
            ConversionError: if an unknown time unit or an unsupported format is used, logged with level "ERROR"
        """
        string = string.strip()
        if TIME_SPAN_REGEX.fullmatch(string) is None:
            raise log_error(ConversionError(FameTime._INVALID_SPAN_FORMAT.format(string)))
        multiple, unit_name = string.split()
        unit_name = unit_name.upper()
        if not unit_name.endswith("S"):
            unit_name += "S"
        try:
            unit = TimeUnit[unit_name]
        except KeyError as e:
            raise log_error(ConversionError(FameTime._INVALID_TIME_UNIT.format(unit_name))) from e
        return FameTime.convert_time_span_to_fame_time_steps(int(multiple), unit)

    @staticmethod
    def is_datetime(string: Any) -> bool:
        """Returns `True` if given `string` matches Datetime string format and can be converted to FAME time step."""
        if isinstance(string, str):
            return DATE_REGEX.fullmatch(string.strip()) is not None
        return False

    @staticmethod
    def is_fame_time_compatible(value: int | str) -> bool:
        """Returns `True` if given int or string `value` can be converted to a FAME time step."""
        if isinstance(value, int):
            return True
        if isinstance(value, str):
            return FameTime.is_datetime(value) or FameTime._is_integer(value)
        return False

    @staticmethod
    def _is_integer(string: str) -> bool:
        """Returns `True` if given string can be interpreted as integer."""
        try:
            int(string)
        except ValueError:
            return False
        return True

    @staticmethod
    def convert_string_if_is_datetime(value: int | str) -> int:
        """Returns FAME time steps of given `value`.

        If it is a valid FAME datetime string it is converted to FAME time steps.
        Else if given `value` is an integer, it is returned without modification.

        Args:
            value: to be converted

        Returns:
            FAME time steps equivalent of provided value

        Raises:
            ConversionError: if given `value` is neither a FAME datetime string nor an integer value,
                logged with level "ERROR"
        """
        if FameTime.is_datetime(value):
            return int(FameTime.convert_datetime_to_fame_time_step(value))  # type: ignore[arg-type]
        try:
            return int(value)
        except ValueError as e:
            raise log_error(ConversionError(FameTime._NO_TIMESTAMP.format(value))) from e

    @staticmethod
    def get_first_fame_time_step_of_year(year: int) -> int:
        """Returns FAME time in integer format of first time step of given year.

        Args:
            year: to get the first time step for

        Returns:
            first time step in the requested year in integer format
        """
        return (year - FAME_FIRST_DATETIME.year) * Constants.STEPS_PER_YEAR
