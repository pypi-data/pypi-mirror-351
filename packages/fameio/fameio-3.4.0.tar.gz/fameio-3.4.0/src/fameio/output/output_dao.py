# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Iterable

import pandas as pd
from fameprotobuf.data_storage_pb2 import DataStorage
from fameprotobuf.services_pb2 import Output

from fameio.output.agent_type import AgentTypeLog
from fameio.output.data_transformer import DataTransformer


class OutputDAO:
    """Grants convenient access to content of Output protobuf messages for given DataStorages."""

    def __init__(self, data_storages: list[DataStorage], agent_type_log: AgentTypeLog) -> None:
        """
        Initialise a new OutputDAO

        Args:
            data_storages: to grant access to by this DAO
            agent_type_log: new types of agents that might come up in the associated data_storages

        Raises:
            AgentTypeError: if duplicate agent definitions occur, logged with level "ERROR"
        """
        self._agent_type_log = agent_type_log
        outputs = self._extract_output_from_data_storages(data_storages)
        self._agent_type_log.update_agents(self._extract_new_agent_types(outputs))
        self._all_series = self._extract_series(outputs)

    @staticmethod
    def _extract_output_from_data_storages(data_storages: list[DataStorage]) -> list[Output]:
        """Returns list of Outputs extracted from given `data_storages`."""
        if data_storages is None:
            data_storages = []
        return [data_storage.output for data_storage in data_storages if data_storage.HasField("output")]

    @staticmethod
    def _extract_new_agent_types(outputs: list[Output]) -> dict[str, Output.AgentType]:
        """Returns dict of agent names mapped to its type defined in given `outputs`."""
        list_of_agent_type_lists = [output.agent_types for output in outputs if len(output.agent_types) > 0]
        list_of_agent_types = [item for sublist in list_of_agent_type_lists for item in sublist]
        return {item.class_name: item for item in list_of_agent_types}

    @staticmethod
    def _extract_series(outputs: list[Output]) -> dict[str, list[Output.Series]]:
        """Returns series data from associated `outputs` mapped to the className of its agent."""
        list_of_series_lists = [output.series for output in outputs if len(output.series) > 0]
        list_of_series = [series for sublist in list_of_series_lists for series in sublist]

        series_per_class_name: dict[str, list[Output.Series]] = {}
        for series in list_of_series:
            if series.class_name not in series_per_class_name:
                series_per_class_name[series.class_name] = []
            series_per_class_name[series.class_name].append(series)
        return series_per_class_name

    def get_sorted_agents_to_extract(self) -> Iterable[str]:
        """Returns iterator of requested and available agent names in ascending order by count of series."""
        all_series = self._get_agent_names_by_series_count_ascending()
        filtered_series = [agent_name for agent_name in all_series if self._agent_type_log.is_requested(agent_name)]
        return iter(filtered_series)

    def _get_agent_names_by_series_count_ascending(self) -> list[str]:
        """Returns list of agent type names sorted by their amount of series"""
        length_per_agent_types = {agent_name: len(value) for agent_name, value in self._all_series.items()}
        sorted_dict = sorted(length_per_agent_types.items(), key=lambda item: item[1])
        return [agent_name for agent_name, _ in sorted_dict]

    def get_agent_data(self, agent_name: str, data_transformer: DataTransformer) -> dict[str | None, pd.DataFrame]:
        """Returns DataFrame(s) containing all data of given `agent` - data is removed after the first call.

        Depending on the chosen ResolveOption the dict contains one DataFrame for the simple (and merged columns),
        or, in `SPLIT` mode, additional DataFrames mapped to each complex column's name.

        Args:
            agent_name: name of agent whose data are to be returned
            data_transformer: to handle data transformation

        Returns:
            output data for requested agent: on data frame for all simple columns, any one for each complex column

        Raises:
            AgentTypeError: if type of agent was not yet registered, logged with level "ERROR"
        """
        agent_series = self._all_series.pop(agent_name) if agent_name in self._all_series else []
        agent_type = self._agent_type_log.get_agent_type(agent_name)
        extracted_data = data_transformer.extract_agent_data(agent_series, agent_type)
        if None in extracted_data and extracted_data[None].empty:
            extracted_data.pop(None)
        return extracted_data
