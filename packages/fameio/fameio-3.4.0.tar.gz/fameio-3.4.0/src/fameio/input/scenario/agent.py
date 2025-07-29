# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import ast
from typing import Any, Final

from fameio.input.metadata import Metadata
from fameio.logs import log
from fameio.tools import keys_to_lower
from .attribute import Attribute
from .exception import assert_or_raise, get_or_raise


class Agent(Metadata):
    """Contains specifications for an agent in a scenario."""

    KEY_TYPE: Final[str] = "Type".lower()
    KEY_ID: Final[str] = "Id".lower()
    KEY_ATTRIBUTES: Final[str] = "Attributes".lower()
    KEY_EXT: Final[str] = "Ext".lower()
    RESERVED_KEYS: set[str] = {KEY_TYPE, KEY_ID, KEY_ATTRIBUTES, KEY_EXT, Metadata.KEY_METADATA}

    _ERR_MISSING_KEY = "Agent definition requires key '{}' but is missing it."
    _ERR_TYPE_EMPTY = "Agent `type` must not be empty."
    _ERR_ILLEGAL_ID = "Agent requires a positive integer `id` but was '{}'."
    _ERR_DOUBLE_ATTRIBUTE = "Cannot add attribute '{}' to agent {} because it already exists."
    _ERR_ATTRIBUTE_OVERWRITE = "Agent's attributes are already set and would be overwritten."
    _WARN_UNEXPECTED_KEY = "Ignoring unexpected key(s) {} in top level of agent with id: {}"

    def __init__(self, agent_id: int, type_name: str, metadata: dict | None = None) -> None:
        """Constructs a new Agent."""
        super().__init__({Agent.KEY_METADATA: metadata} if metadata else None)
        assert_or_raise(isinstance(agent_id, int) and agent_id >= 0, self._ERR_ILLEGAL_ID.format(agent_id))
        assert_or_raise(bool(type_name and type_name.strip()), self._ERR_TYPE_EMPTY)
        self._id: int = agent_id
        self._type_name: str = type_name.strip()
        self._attributes: dict[str, Attribute] = {}

    @classmethod
    def from_dict(cls, definitions: dict) -> Agent:
        """Create new Agent from given `definitions`

        Args:
            definitions: dictionary representation of an agent

        Returns:
            new agent created from `definitions`

        Raises:
            ScenarioError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        definitions = keys_to_lower(definitions)
        agent_type = get_or_raise(definitions, Agent.KEY_TYPE, Agent._ERR_MISSING_KEY)
        agent_id = get_or_raise(definitions, Agent.KEY_ID, Agent._ERR_MISSING_KEY)
        Agent.validate_keys(definitions, agent_id)
        metadata = definitions.get(Agent.KEY_METADATA, None)
        agent = cls(agent_id, agent_type, metadata)
        agent.init_attributes_from_dict(definitions.get(Agent.KEY_ATTRIBUTES, {}))
        return agent

    @staticmethod
    def validate_keys(data: dict, agent_id: int) -> None:
        """Logs a warning if any unexpected keys are presented at top level of `data`.

        Expected keys are defined in `Agent.RESERVED_KEYS`

        Args:
            data: agent definition to be checked
            agent_id: id of agent to be checked
        """
        unexpected_keys = set(data.keys()) - Agent.RESERVED_KEYS
        if unexpected_keys:
            log().warning(Agent._WARN_UNEXPECTED_KEY.format(unexpected_keys, agent_id))

    def init_attributes_from_dict(self, attributes: dict[str, Any]) -> None:
        """Initialise agent `attributes` from dict.

        Must only be called when creating a new Agent.

        Args:
            attributes: to be set

        Raises:
            ScenarioError: if attributes were already initialised
        """
        assert_or_raise(not self._attributes, self._ERR_ATTRIBUTE_OVERWRITE)
        self._attributes = {}
        for name, value in attributes.items():
            full_name = f"{self.type_name}({self.id}): {name}"
            self.add_attribute(name, Attribute(full_name, value))

    def add_attribute(self, name: str, value: Attribute) -> None:
        """Adds a new attribute to the Agent (raise an error if it already exists)."""
        if name in self._attributes:
            raise ValueError(self._ERR_DOUBLE_ATTRIBUTE.format(name, self.display_id))
        self._attributes[name] = value
        self._notify_data_changed()

    def _to_dict(self) -> dict:
        """Serializes the Agent's content to a dict."""
        result = {Agent.KEY_TYPE: self.type_name, Agent.KEY_ID: self.id}
        if self._attributes:
            result[self.KEY_ATTRIBUTES] = {name: value.to_dict() for name, value in self._attributes.items()}
        return result

    def to_string(self) -> str:
        """Serializes this agent to a string."""
        return repr(self.to_dict())

    @classmethod
    def from_string(cls, definitions: str) -> Agent:
        return cls.from_dict(ast.literal_eval(definitions))

    def _notify_data_changed(self):
        """Placeholder method used to signal data changes to derived types."""

    @property
    def id(self) -> int:
        """Returns the ID of the Agent."""
        return self._id

    @property
    def display_id(self) -> str:
        """Returns the ID of the Agent as a string for display purposes."""
        return f"#{self._id}"

    @property
    def type_name(self) -> str:
        """Returns the name of the Agent type."""
        return self._type_name

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Returns dictionary of all Attributes of this agent."""
        return self._attributes
