# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import ast
from typing import Any, Final

from fameio.input import SchemaError
from fameio.logs import log_error
from fameio.tools import keys_to_lower
from .agenttype import AgentType
from .java_packages import JavaPackages


class Schema:
    """Definition of a schema."""

    KEY_AGENT_TYPE: Final[str] = "AgentTypes".lower()
    KEY_PACKAGES: Final[str] = "JavaPackages".lower()

    _ERR_AGENT_TYPES_MISSING = "Required keyword `AgentTypes` missing in Schema."
    _ERR_AGENT_TYPES_EMPTY = "`AgentTypes` must not be empty - at least one type of agent is required."
    _ERR_MISSING_PACKAGES = "Missing required section `JavaPackages` in Schema."

    def __init__(self, definitions: dict) -> None:
        self._original_input_dict = definitions
        self._agent_types: dict[str, AgentType] = {}
        self._packages: JavaPackages | None = None

    @classmethod
    def from_dict(cls, definitions: dict) -> Schema:
        """Convert given `definitions` into a new schema.

        Args:
            definitions: dictionary representation of schema

        Returns:
            schema created from given definitions

        Raises:
            SchemaError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        definitions = keys_to_lower(definitions)
        schema = cls(definitions)

        agent_types = cls._get_or_raise(definitions, Schema.KEY_AGENT_TYPE, Schema._ERR_AGENT_TYPES_MISSING)
        if len(agent_types) == 0:
            raise log_error(SchemaError(Schema._ERR_AGENT_TYPES_EMPTY))
        for agent_type_name, agent_definition in agent_types.items():
            agent_type = AgentType.from_dict(agent_type_name, agent_definition)
            schema._agent_types[agent_type_name] = agent_type

        java_packages = cls._get_or_raise(definitions, Schema.KEY_PACKAGES, Schema._ERR_MISSING_PACKAGES)
        schema._packages = JavaPackages.from_dict(java_packages)

        return schema

    @staticmethod
    def _get_or_raise(definitions: dict[str, Any], key: str, error_message: str) -> Any:
        """Get given `key` from given `definitions` - raise error with given `error_message` if not present.

        Args:
            definitions: to search the key in
            key: to be searched
            error_message: to be logged and included in the raised exception if key is missing

        Returns:
            value associated with given key in given definitions

        Raises:
            SchemaError: if given key is not in given definitions, logged on level "ERROR"
        """
        if key not in definitions:
            raise log_error(SchemaError(error_message))
        return definitions[key]

    @classmethod
    def from_string(cls, definitions: str) -> Schema:
        """Load given string `definitions` into a new Schema."""
        return cls.from_dict(ast.literal_eval(definitions))

    def to_dict(self) -> dict:
        """Serializes the schema content to a dict."""
        return self._original_input_dict

    def to_string(self) -> str:
        """Returns a string representation of the Schema of which the class can be rebuilt."""
        return repr(self.to_dict())

    @property
    def agent_types(self) -> dict[str, AgentType]:
        """Returns all the agent types by their name."""
        return self._agent_types

    @property
    def packages(self) -> JavaPackages:
        """Returns JavaPackages, i.e. names where model classes are defined in."""
        if self._packages is None:
            raise log_error(SchemaError(self._ERR_MISSING_PACKAGES))
        return self._packages
