# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from fameprotobuf.services_pb2 import Output

from fameio.logs import log_error
from fameio.output import OutputError


class AgentType:
    """Provides information derived from an underlying protobuf AgentType."""

    def __init__(self, agent_type: Output.AgentType) -> None:
        self._agent_type = agent_type

    def get_simple_column_map(self) -> dict[int, str]:
        """Returns dictionary of simple column IDs mapped to their name - ignoring complex columns"""
        return {field.field_id: field.field_name for field in self._agent_type.fields if len(field.index_names) == 0}

    def get_merged_column_map(self) -> dict[int, str]:
        """Returns dictionary of all column IDs mapped to their name merged with names of inner complex columns"""
        column_names = {}
        for field in self._agent_type.fields:
            if len(field.index_names) == 0:
                column_names[field.field_id] = field.field_name
            else:
                column_names[field.field_id] = f"{field.field_name}_({tuple(field.index_names)}, value)"
        return column_names

    def get_simple_column_mask(self) -> list[bool]:
        """Returns list of bool - where an entry is True if the output column with the same index is not complex"""
        return [len(field.index_names) == 0 for field in self._agent_type.fields]

    def get_complex_column_ids(self) -> set[int]:
        """Returns set of IDs for complex columns, ignoring simple columns"""
        return {field.field_id for field in self._agent_type.fields if len(field.index_names) > 0}

    def get_column_name_for_id(self, column_index: int) -> str | None:
        """Returns name of column by given `column_index` or None, if column is not present"""
        if 0 <= column_index < len(self._agent_type.fields):
            return self._agent_type.fields[column_index].field_name
        return None

    def get_inner_columns(self, column_index: int) -> tuple[str, ...]:
        """Returns tuple of inner column names for complex column with given `column_index`"""
        return tuple(self._agent_type.fields[column_index].index_names)

    def get_class_name(self) -> str:
        """Returns name of class of wrapped agent type"""
        return self._agent_type.class_name


class AgentTypeError(OutputError):
    """Indicates an error with the agent types definitions."""


class AgentTypeLog:
    """Stores data about collected agent types."""

    _ERR_AGENT_TYPE_MISSING = "Requested AgentType `{}` not found."
    _ERR_DOUBLE_DEFINITION = "Just one definition allowed per AgentType. Found multiple for {}. File might be corrupt."

    def __init__(self, _agent_name_filter_list: list[str]) -> None:
        """Initialises new AgentTypeLog.

        Args:
            _agent_name_filter_list: list of agent type names that are requested for output data extraction
        """
        self._agent_name_filter_list: list[str] | None = (
            [agent.upper() for agent in _agent_name_filter_list] if _agent_name_filter_list else None
        )
        self._requested_agent_types: dict[str, AgentType] = {}
        self._agents_with_output: list[str] = []

    def update_agents(self, new_types: dict[str, Output.AgentType]) -> None:
        """Saves `new_types` if they are requested for extraction.

        If any new agent types are provided, checks if they are requested for extraction, and, if so, saves them.
        Agent types not requested for extraction are ignored.

        Args:
            new_types: to be saved (if requested for extraction)

        Raises:
            AgentTypeError: if agent type was already registered, logged with level "ERROR"
        """
        if not new_types:
            return

        self._agents_with_output.extend(list(new_types.keys()))
        filtered_types = self._filter_agents_by_name(new_types)
        self._ensure_no_duplication(filtered_types)
        self._requested_agent_types.update(filtered_types)

    def _filter_agents_by_name(self, new_types: dict[str, Output.AgentType]) -> dict[str, Output.AgentType]:
        """Removes and entries from `new_types` not on `agent_name_filter_list`.

        Args:
            new_types: to be filtered

        Returns:
            filtered list, or original list if no filter is active
        """
        if self._agent_name_filter_list:
            return {
                agent_name: agent_type
                for agent_name, agent_type in new_types.items()
                if agent_name.upper() in self._agent_name_filter_list
            }
        return new_types

    def _ensure_no_duplication(self, filtered_types: dict[str, Output.AgentType]) -> None:
        """Ensures no duplicate agent type definitions occur.

        Args:
            filtered_types: to be checked for duplications with already registered types

        Raises:
            AgentTypeError: if duplicate agent type is found, logged with level "ERROR"
        """
        for agent_name in self._requested_agent_types:
            if agent_name in filtered_types:
                raise log_error(AgentTypeError(self._ERR_DOUBLE_DEFINITION.format(agent_name)))

    def has_any_agent_type(self) -> bool:
        """Returns True if any agent type was registered so far present."""
        return len(self._requested_agent_types) > 0

    def get_agent_type(self, agent_type_name: str) -> AgentType:
        """Returns the requested type of agent.

        Args:
            agent_type_name: requested name of agent type

        Returns:
            stored agent type

        Raises:
            AgentTypeError: if no agent type could be found with that name, logged with level "ERROR"
        """
        if agent_type_name not in self._requested_agent_types:
            raise log_error(AgentTypeError(self._ERR_AGENT_TYPE_MISSING.format(agent_type_name)))
        return AgentType(self._requested_agent_types[agent_type_name])

    def is_requested(self, agent_name: str) -> bool:
        """Returns True if given agent_name is known and requested."""
        return agent_name in self._requested_agent_types

    def get_agents_with_output(self) -> list[str]:
        """Returns all names of agents that had output."""
        return self._agents_with_output
