# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import math

import pandas as pd

from fameio.cli.options import TimeOptions
from fameio.logs import log_error, log
from fameio.output import OutputError
from fameio.time import FameTime, ConversionError as TimeConversionError

_ERR_UNIMPLEMENTED = "Time conversion mode '{}' not implemented."
_ERR_TIME_CONVERSION = "Conversion of timestamps failed."
_ERR_NEGATIVE = "StepsBefore and StepsAfter must be Zero or positive integers"


class ConversionError(OutputError):
    """An error that occurred during conversion of output data."""


def apply_time_merging(data: dict[str | None, pd.DataFrame], config: list[int] | None) -> None:
    """Applies merging of TimeSteps inplace for given `data`.

    Args:
        data: one or multiple DataFrames of time series; depending on the given config, contents might be modified
        config: three integer values defining how to merge data within a range of time steps

    Raises:
        ConversionError: if parameters are not valid, logged with level "ERROR"
    """
    if not config or all(v == 0 for v in config):
        return
    focal_point, steps_before, steps_after = config
    if steps_before < 0 or steps_after < 0:
        raise log_error(ConversionError(_ERR_NEGATIVE))

    period = steps_before + steps_after + 1
    first_positive_focal_point = focal_point % period
    _apply_time_merging(data, offset=steps_before, period=period, first_positive_focal_point=first_positive_focal_point)


def _apply_time_merging(
    dataframes: dict[str | None, pd.DataFrame], offset: int, period: int, first_positive_focal_point: int
) -> None:
    """Applies time merging to `data` based on given `offset`, `period`, and `first_positive_focal_point`."""
    log().debug("Grouping TimeSteps...")
    for key in dataframes.keys():
        df = dataframes[key]
        index_columns = df.index.names
        df.reset_index(inplace=True)
        df["TimeStep"] = df["TimeStep"].apply(lambda t: _merge_time(t, first_positive_focal_point, offset, period))
        dataframes[key] = df.groupby(by=index_columns).sum()


def _merge_time(time_step: int, focal_time: int, offset: int, period: int) -> int:
    """Returns `time_step` rounded to its corresponding focal point.

    Args:
        time_step: TimeStep to round
        focal_time: First positive focal point
        offset: Range of TimeSteps left of the focal point
        period: Total range of TimeSteps belonging to the focal point

    Returns:
        Corresponding focal point
    """
    return math.floor((time_step + offset - focal_time) / period) * period + focal_time


def apply_time_option(data: dict[str | None, pd.DataFrame], mode: TimeOptions) -> None:
    """Applies time option based on given `mode` inplace of given `data`.

    Args:
        data: one or multiple DataFrames of time series; column `TimeStep` might be modified (depending on mode)
        mode: name of time conversion mode (derived from Enum)

    Raises:
        ConversionError: if provided mode is not implemented , logged with level "ERROR"
    """
    try:
        if mode == TimeOptions.INT:
            log().debug("No time conversion...")
        elif mode == TimeOptions.UTC:
            _convert_time_index(data, "%Y-%m-%d %H:%M:%S")
        elif mode == TimeOptions.FAME:
            _convert_time_index(data, "%Y-%m-%d_%H:%M:%S")
        else:
            raise log_error(ConversionError(_ERR_UNIMPLEMENTED.format(mode)))
    except TimeConversionError as e:
        raise log_error(ConversionError(_ERR_TIME_CONVERSION.format())) from e


def _convert_time_index(data: dict[str | None, pd.DataFrame], datetime_format: str) -> None:
    """Replaces (inplace) `TimeStep` column in MultiIndex of each item of `data` to DateTime.

    Format of the resulting DateTime is determined by given `date_format`.

    Args:
        data: one or multiple DataFrames of time series; column `TimeStep` will be modified
        datetime_format: determines result of the conversion

    Raises:
        TimeConversionError: if time cannot be converted, logged with level "ERROR"
    """
    log().debug(f"Converting TimeStep to format '{datetime_format}'...")
    for _, df in data.items():
        index_columns = df.index.names
        df.reset_index(inplace=True)
        df["TimeStep"] = df["TimeStep"].apply(lambda t: FameTime.convert_fame_time_step_to_datetime(t, datetime_format))
        df.set_index(keys=index_columns, inplace=True)
