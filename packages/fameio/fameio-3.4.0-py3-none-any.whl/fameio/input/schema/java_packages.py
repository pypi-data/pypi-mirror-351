# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Final

from fameio.input import SchemaError
from fameio.logs import log, log_error
from fameio.tools import keys_to_lower


class JavaPackages:
    """Schema definitions for Java package names in which model classes reside."""

    KEY_AGENT: Final[str] = "Agents".lower()
    KEY_DATA_ITEM: Final[str] = "DataItems".lower()
    KEY_PORTABLE: Final[str] = "Portables".lower()

    _ERR_MISSING_AGENTS = "JavaPackages requires non-empty list for `Agents`. Key was missing or list was empty."
    _INFO_MISSING_DATA_ITEMS = "`DataItems` not specified: Key was missing or list was empty."
    _ERR_MISSING_PORTABLES = "JavaPackages require non-empty list for `Portables`. Key was missing or list was empty."

    def __init__(self) -> None:
        self._agents: list[str] = []
        self._data_items: list[str] = []
        self._portables: list[str] = []

    @classmethod
    def from_dict(cls, definitions: dict[str, list[str]]) -> JavaPackages:
        """Creates JavaPackages from a dictionary representation.

        Args:
            definitions: dictionary representation of JavaPackages

        Returns:
            new instance of JavaPackages

        Raises:
            SchemaError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        java_packages = cls()
        definitions = keys_to_lower(definitions)

        java_packages._agents = definitions.get(JavaPackages.KEY_AGENT, [])
        java_packages._data_items = definitions.get(JavaPackages.KEY_DATA_ITEM, [])
        java_packages._portables = definitions.get(JavaPackages.KEY_PORTABLE, [])

        if not java_packages._agents:
            raise log_error(SchemaError(JavaPackages._ERR_MISSING_AGENTS))
        if not java_packages._data_items:
            log().info(JavaPackages._INFO_MISSING_DATA_ITEMS)
        if not java_packages._portables:
            raise log_error(SchemaError(JavaPackages._ERR_MISSING_PORTABLES))

        return java_packages

    @property
    def agents(self) -> list[str]:
        """Return list of java package names that contain the model's Agents."""
        return self._agents

    @property
    def data_items(self) -> list[str]:
        """Return list of java package names that contain the model's DataItems."""
        return self._data_items

    @property
    def portables(self) -> list[str]:
        """Return list of java package names that contain the model's Portables."""
        return self._portables

    def to_dict(self) -> dict[str, list[str]]:
        """Return dictionary representation of this JavaPackages object."""
        return {self.KEY_AGENT: self.agents, self.KEY_DATA_ITEM: self.data_items, self.KEY_PORTABLE: self.portables}
