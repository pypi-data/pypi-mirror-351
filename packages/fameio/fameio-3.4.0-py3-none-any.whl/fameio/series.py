# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import math
import os
from enum import Enum, auto
from pathlib import Path
from typing import Any

import pandas as pd
from fameprotobuf.input_file_pb2 import InputData
from google.protobuf.internal.wire_format import INT64_MIN, INT64_MAX

from fameio.input import InputError
from fameio.input.resolver import PathResolver
from fameio.logs import log, log_error
from fameio.output import OutputError
from fameio.time import ConversionError, FameTime
from fameio.tools import clean_up_file_name, CSV_FILE_SUFFIX


FILE_LENGTH_WARN_LIMIT = int(50e3)


class TimeSeriesError(InputError, OutputError):
    """Indicates that an error occurred during management of time series"""


class Entry(Enum):
    ID = auto()
    NAME = auto()
    DATA = auto()


class TimeSeriesManager:
    """Manages matching of files to time series ids and their protobuf representation."""

    _TIMESERIES_RECONSTRUCTION_PATH = "./timeseries/"
    _CONSTANT_IDENTIFIER = "Constant value: {}"
    _KEY_ROW_TIME = "timeStep"
    _KEY_ROW_VALUE = "value"

    _ERR_FILE_NOT_FOUND = "Cannot find Timeseries file '{}'."
    _ERR_NUMERIC_STRING = " Remove quotes to use a constant numeric value instead of a timeseries file."
    _ERR_CORRUPT_KEYS = "TimeSeries file '{}' corrupt: At least one entry in first column isn't a timestamp."
    _ERR_CORRUPT_VALUES = "TimeSeries file '{}' corrupt: At least one entry in second column isn't numeric."
    _ERR_NON_NUMERIC = "Values in TimeSeries must be numeric but was: '{}'"
    _ERR_NAN_VALUE = "Values in TimeSeries must not be missing or NaN."
    _ERR_UNREGISTERED_SERIES = "No timeseries registered with identifier '{}' - was the Scenario validated?"
    _ERR_UNREGISTERED_SERIES_RE = "No timeseries registered with identifier '{}' - were the timeseries reconstructed?"
    _WARN_NO_DATA = "No timeseries stored in timeseries manager. Double check if you expected timeseries."
    _WARN_DATA_IGNORED = "Timeseries '{}' contains additional columns with data which will be ignored."
    _WARN_LARGE_CONVERSION = (
        "Timeseries file '{}' is large and needs conversion of time stamps. If performance "
        "issues occur and the file is reused, convert the time stamp column once with "
        "`fameio.time.FameTime.convert_datetime_to_fame_time_step(datetime_string)`."
    )

    def __init__(self, path_resolver: PathResolver = PathResolver()) -> None:
        self._path_resolver = path_resolver
        self._id_count = -1
        self._series_by_id: dict[str | int | float, dict[Entry, Any]] = {}

    def register_and_validate(self, identifier: str | int | float) -> None:
        """Registers given timeseries `identifier` and validates associated timeseries.

        Args:
            identifier: to be registered - either a single numeric value or a string pointing to a timeseries file

        Raises:
            TimeSeriesError: if the file could not be found or contains improper data, or if identifier is NaN,
                logged with level "ERROR"
        """
        if not self._time_series_is_registered(identifier):
            self._register_time_series(identifier)

    def _time_series_is_registered(self, identifier: str | int | float) -> bool:
        """Returns True if the value was already registered."""
        return identifier in self._series_by_id

    def _register_time_series(self, identifier: str | int | float) -> None:
        """Assigns an id to the given `identifier` and loads the time series into a dataframe.

        Args:
            identifier: to be registered - either a single numeric value or a string pointing to a timeseries file

        Raises:
            TimeSeriesError: if the file could not be found or contains improper data, or if identifier is NaN,
                logged with level "ERROR"
        """
        self._id_count += 1
        name, series = self._get_name_and_dataframe(identifier)
        self._series_by_id[identifier] = {Entry.ID: self._id_count, Entry.NAME: name, Entry.DATA: series}

    def _get_name_and_dataframe(self, identifier: str | int | float) -> tuple[str, pd.DataFrame]:
        """Returns name and DataFrame containing the series obtained from the given `identifier`.

        Args:
            identifier: to be registered - either a single numeric value or a string pointing to a timeseries file

        Returns:
            tuple of name & dataframe

        Raises:
            TimeSeriesError: if the file could not be found or contains improper data, or if identifier is NaN,
                logged with level "ERROR"
        """
        if isinstance(identifier, str):
            series_path = self._path_resolver.resolve_series_file_path(Path(identifier).as_posix())
            if series_path and os.path.exists(series_path):
                data = self.read_timeseries_file(series_path)
                return identifier, self.check_and_convert_series(data, identifier)
            message = self._ERR_FILE_NOT_FOUND.format(identifier)
            if self._is_number_string(identifier):
                message += self._ERR_NUMERIC_STRING
            raise log_error(TimeSeriesError(message))
        return self._create_timeseries_from_value(identifier)

    @staticmethod
    def read_timeseries_file(file: Path | str) -> pd.DataFrame:
        """Loads a timeseries from file.

        Args:
            file: to be read

        Returns:
            data frame obtained from file

        Raises:
            TimeSeriesError: if file could not be read, logged with level "ERROR"
        """
        try:
            return pd.read_csv(file, sep=";", header=None, comment="#")
        except OSError as e:
            raise log_error(TimeSeriesError(e)) from e

    @staticmethod
    def check_and_convert_series(data: pd.DataFrame, file_name: str, warn: bool = True) -> pd.DataFrame:
        """Ensures validity of time series and convert to required format for writing to disk.

        Args:
            data: dataframe to be converted to expected format
            file_name: used in warnings and errors
            warn: if True, a warning is raised if large files require conversion (default: True)

        Returns:
            2-column dataframe, first column: integers, second column: floats (no NaN)

        Raises:
            TimeSeriesError: if the data do not correspond to a valid time series, logged with level "ERROR"
        """
        try:
            converted, large_conversion = TimeSeriesManager._check_and_convert_series(data, file_name)
            if large_conversion and warn:
                log().warning(TimeSeriesManager._WARN_LARGE_CONVERSION.format(file_name))
            return converted
        except TypeError as e:
            raise log_error(TimeSeriesError(TimeSeriesManager._ERR_CORRUPT_VALUES.format(file_name), e)) from e
        except ConversionError as e:
            raise log_error(TimeSeriesError(TimeSeriesManager._ERR_CORRUPT_KEYS.format(file_name), e)) from e

    @staticmethod
    def _check_and_convert_series(data: pd.DataFrame, file_name: str) -> tuple[pd.DataFrame, bool]:
        """Ensures validity of time series and convert to required format for writing to disk.

        Args:
            data: dataframe to be converted to expected format
            file_name: used in warnings

        Returns:
            tuple of 1) dataframe and 2) large conversion indicator:
                2-column dataframe first column: integers, second column: floats (no NaN)
                large conversion indicator: if true, the timeseries was large and required conversion

        Raises:
            ConversionError: if first data column could not be converted to integer, logged with level "ERROR"
            TypeError: if second data column in given data could not be converted to float or contained NaN,
                logged with level "ERROR"
        """
        large_file_indicator = False
        data, additional_columns = data.loc[:, :2], data.loc[:, 2:]
        if not additional_columns.dropna(how="all").empty:
            log().warning(TimeSeriesManager._WARN_DATA_IGNORED.format(file_name))
        if data.dtypes[0] != "int64":
            if len(data[0]) > FILE_LENGTH_WARN_LIMIT:
                large_file_indicator = True
            data[0] = [FameTime.convert_string_if_is_datetime(time) for time in data[0]]
        if data.dtypes[1] != "float64":
            data[1] = [TimeSeriesManager._assert_float(value) for value in data[1]]
        if data[1].isna().any():
            raise log_error(TypeError(TimeSeriesManager._ERR_NAN_VALUE))
        return data, large_file_indicator

    @staticmethod
    def _assert_float(value: Any) -> float:
        """Converts any given value to a float or raise an Exception.

        Args:
            value: to be converted to float

        Returns:
            float representation of value

        Raises:
            TypeError: if given value cannot be converted to float, logged with level "ERROR"
        """
        try:
            value = float(value)
        except ValueError as e:
            raise log_error(TypeError(TimeSeriesManager._ERR_NON_NUMERIC.format(value))) from e
        return value

    @staticmethod
    def _is_number_string(identifier: str) -> bool:
        """Returns True if given identifier can be cast to float."""
        try:
            float(identifier)
            return True
        except ValueError:
            return False

    @staticmethod
    def _create_timeseries_from_value(value: int | float) -> tuple[str, pd.DataFrame]:
        """Returns name and dataframe for a new static timeseries created from the given `value`.

        Args:
            value: the static value of the timeseries to be created

        Returns:
            tuple of name & dataframe

        Raises:
            TimeSeriesError: if given value is NaN, logged with level "ERROR"
        """
        if math.isnan(value):
            raise log_error(TimeSeriesError(TimeSeriesManager._ERR_NAN_VALUE))
        data = pd.DataFrame({0: [INT64_MIN, INT64_MAX], 1: [value, value]})
        return TimeSeriesManager._CONSTANT_IDENTIFIER.format(value), data

    def get_series_id_by_identifier(self, identifier: str | int | float) -> int:
        """Returns id for a previously stored time series by given `identifier`.

        Args:
            identifier: to get the unique ID for

        Returns:
            unique ID for the given identifier

        Raises:
            TimeSeriesError: if identifier was not yet registered, logged with level "ERROR"
        """
        if not self._time_series_is_registered(identifier):
            raise log_error(TimeSeriesError(self._ERR_UNREGISTERED_SERIES.format(identifier)))
        return self._series_by_id.get(identifier)[Entry.ID]  # type: ignore[index]

    def get_all_series(self) -> list[tuple[int, str, pd.DataFrame]]:
        """Returns iterator over id, name and dataframe of all stored series."""
        if len(self._series_by_id) == 0:
            log().warning(self._WARN_NO_DATA)
        return [(v[Entry.ID], v[Entry.NAME], v[Entry.DATA]) for v in self._series_by_id.values()]

    def reconstruct_time_series(self, timeseries: list[InputData.TimeSeriesDao]) -> None:
        """Reconstructs and stores time series from given list of `timeseries_dao`."""
        for one_series in timeseries:
            self._id_count += 1
            reconstructed = {Entry.ID: one_series.series_id}
            if len(one_series.values) == 1 or (
                len(one_series.values) == 2 and one_series.values[0] == one_series.values[1]
            ):
                reconstructed[Entry.NAME] = one_series.values[0]
                reconstructed[Entry.DATA] = None
            else:
                reconstructed[Entry.NAME] = self._get_cleaned_file_name(one_series.series_name)
                reconstructed[Entry.DATA] = pd.DataFrame(
                    {self._KEY_ROW_TIME: list(one_series.time_steps), self._KEY_ROW_VALUE: list(one_series.values)}
                )
            self._series_by_id[one_series.series_id] = reconstructed

    def _get_cleaned_file_name(self, timeseries_name: str) -> str:
        """Ensure given file name has CSV file ending."""
        if Path(timeseries_name).suffix.lower() == CSV_FILE_SUFFIX:
            filename = Path(timeseries_name).name
        else:
            filename = clean_up_file_name(timeseries_name) + CSV_FILE_SUFFIX
        return str(Path(self._TIMESERIES_RECONSTRUCTION_PATH, filename))

    def get_reconstructed_series_by_id(self, series_id: int) -> str:
        """Return name or path for given `series_id` if series these are identified by their number.

        Use this only if series were added via `reconstruct_time_series`

        Args:
            series_id: number of series

        Returns:
            name or path of time series

        Raises:
            TimeSeriesError: if series was not registered during `reconstruct_time_series`, logged with level "ERROR"
        """
        if series_id < 0 or series_id > self._id_count:
            raise log_error(TimeSeriesError(self._ERR_UNREGISTERED_SERIES_RE.format(series_id)))
        return self._series_by_id[series_id][Entry.NAME]
