# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Final, Any, Union

from fameio.input import InputError
from fameio.input.metadata import Metadata, MetadataComponent, ValueContainer
from fameio.logs import log_error
from fameio.tools import keys_to_lower


class StringSet(Metadata):
    """Hosts a StringSet in the given format."""

    class StringSetError(InputError):
        """An error that occurred while parsing a StringSet definition."""

    KEY_VALUES: Final[str] = "Values".lower()

    ValueType = Union[list[str], dict[str, dict]]
    StringSetType = dict[str, Union[dict, ValueType]]

    _ERR_KEY_MISSING = "Missing mandatory key '{}' in StringSet definition {}."
    _ERR_VALUE_DEFINITION = "StringSet could not be parsed."

    def __init__(self, definitions: dict[str, Any] | list[Any] | None = None):
        super().__init__(definitions)
        self._value_container: ValueContainer = ValueContainer(definitions)

    @classmethod
    def from_dict(cls, definition: StringSetType) -> StringSet:
        """Returns StringSet initialised from `definition`.

        Args:
            definition: dictionary representation of string set

        Returns:
            new StringSet

        Raises:
            StringSetError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        string_set = cls(definition)
        definition = keys_to_lower(definition)
        if cls.KEY_VALUES in definition:
            try:
                string_set._value_container = ValueContainer(definition[cls.KEY_VALUES])
            except ValueContainer.ParseError as e:
                raise log_error(StringSet.StringSetError(StringSet._ERR_VALUE_DEFINITION)) from e
        else:
            raise log_error(StringSet.StringSetError(cls._ERR_KEY_MISSING.format(cls.KEY_VALUES, definition)))
        return string_set

    def _to_dict(self) -> dict[str, dict[str, dict[str, dict[str, dict]]]]:
        return {self.KEY_VALUES: self._value_container.to_dict()}

    @property
    def values(self) -> dict[str, MetadataComponent]:
        """Returns values and their associated MetadataComponent."""
        return self._value_container.values

    def is_in_set(self, key: Any) -> bool:
        """Returns True if `key` is a valid name in this StringSet."""
        return self._value_container.has_value(key)
