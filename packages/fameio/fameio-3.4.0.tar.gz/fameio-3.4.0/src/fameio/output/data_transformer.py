# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from abc import ABC

import pandas as pd
from fameprotobuf.services_pb2 import Output
from pandas import DataFrame

from fameio.cli.options import ResolveOptions
from fameio.output.agent_type import AgentType

INDEX = ("AgentId", "TimeStep")


class DataTransformer(ABC):
    """Extracts and provides series data from parsed and processed output files for requested agents."""

    MODES = {
        ResolveOptions.IGNORE: lambda: DataTransformerIgnore(),  # pylint: disable=unnecessary-lambda
        ResolveOptions.SPLIT: lambda: DataTransformerSplit(),  # pylint: disable=unnecessary-lambda
    }
    SIMPLE_COLUMN_INDEX = -1

    @staticmethod
    def build(complex_column_mode: ResolveOptions) -> DataTransformer:
        return DataTransformer.MODES[complex_column_mode]()

    def extract_agent_data(self, series: list[Output.Series], agent_type: AgentType) -> dict[str | None, pd.DataFrame]:
        """Returns dict of DataFrame(s) containing all data from given `series` of given `agent_type`.

        When ResolveOption is `SPLIT`, the dict maps each complex column's name to the associated DataFrame.
        In any case, the dict maps `None` to a DataFrame with the content of all simple columns.
        """
        container = self._extract_agent_data(series, agent_type)
        data_frames = {}
        for column_id, agent_data in container.items():
            data_frame = DataFrame.from_dict(agent_data, orient="index")
            column_name = agent_type.get_column_name_for_id(column_id)
            if column_id == DataTransformer.SIMPLE_COLUMN_INDEX:
                data_frame.rename(columns=self._get_column_map(agent_type), inplace=True)
                index: tuple[str, ...] = INDEX
                data_frame = data_frame.loc[:, agent_type.get_simple_column_mask()]
            else:
                data_frame.rename(columns={0: column_name}, inplace=True)
                index = INDEX + agent_type.get_inner_columns(column_id)

            if not data_frame.empty:
                data_frame.index = pd.MultiIndex.from_tuples(data_frame.index)
                data_frame.rename_axis(index, inplace=True)
            data_frames[column_name] = data_frame
        return data_frames

    def _extract_agent_data(
        self, series: list[Output.Series], agent_type: AgentType
    ) -> dict[int, dict[tuple, list[float | None | str]]]:
        """Returns mapping of (agentId, timeStep) to fixed-length list of all output columns for given `class_name`."""
        container = DataTransformer._create_container(agent_type)
        mask_simple = agent_type.get_simple_column_mask()
        while series:
            self._add_series_data(series.pop(), mask_simple, container)
        filled_columns = {index: column_data for index, column_data in container.items() if len(column_data) > 0}
        return filled_columns

    @staticmethod
    def _create_container(agent_type: AgentType) -> dict[int, dict]:
        """Returns map of complex columns IDs to an empty dict, and one more for the remaining simple columns."""
        field_ids = agent_type.get_complex_column_ids().union([DataTransformer.SIMPLE_COLUMN_INDEX])
        return {field_id: {} for field_id in field_ids}

    def _add_series_data(
        self,
        series: Output.Series,
        mask_simple: list[bool],
        container: dict[int, dict[tuple, list[float | None | str]]],
    ) -> None:
        """Adds data from given `series` to specified `container` dict as list."""
        empty_list: list = [None] * len(mask_simple)
        for line in series.lines:
            index = (series.agent_id, line.time_step)
            simple_values = empty_list.copy()
            for column in line.columns:
                if mask_simple[column.field_id]:
                    simple_values[column.field_id] = column.value
                else:
                    self._store_complex_values(column, container, index)
            container[DataTransformer.SIMPLE_COLUMN_INDEX][index] = simple_values

    @staticmethod
    def _store_complex_values(column: Output.Series.Line.Column, container: dict[int, dict], base_index: tuple) -> None:
        """Stores complex column data."""

    @staticmethod
    def _get_column_map(agent_type: AgentType) -> dict[int, str]:
        """Returns mapping of simple column IDs to their name for given `agent_type`."""
        return agent_type.get_simple_column_map()


class DataTransformerIgnore(DataTransformer):
    """Ignores complex columns on output."""


class DataTransformerSplit(DataTransformer):
    """Stores complex data columns split by column type."""

    @staticmethod
    def _store_complex_values(column: Output.Series.Line.Column, container: dict[int, dict], base_index: tuple) -> None:
        """Adds inner data from `column` to given `container` - split by column type."""
        for entry in column.entries:
            index = base_index + tuple(entry.index_values)
            container[column.field_id][index] = entry.value
