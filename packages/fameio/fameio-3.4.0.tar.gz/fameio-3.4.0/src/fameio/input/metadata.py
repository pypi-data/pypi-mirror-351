# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, final, Final

from fameio.input import InputError
from fameio.logs import log_error


class Metadata(ABC):
    """Hosts metadata of any kind - extend this class to optionally add metadata capability to the extending class."""

    KEY_METADATA: Final[str] = "Metadata".lower()

    def __init__(self, definitions: Any | dict[str, Any] | None = None):
        """Initialises the metadata.

        Search the given definitions' top level for metadata.
        Alternatively, call `_extract_metadata()` to add metadata later on.
        If metadata are found on the definitions, they get removed.
        """
        self._metadata = self.__extract_metadata(definitions)

    @staticmethod
    def __extract_metadata(definitions: dict[str, Any] | None) -> dict:
        """Extract metadata from `definitions` - if present.

        If keyword `metadata` is found on the highest level of given `definitions`, metadata are extracted (removed) and
        returned, otherwise, an empty dict is returned and definitions are not changed.
        """
        if definitions and isinstance(definitions, dict):
            matching_key = [key for key in definitions.keys() if key.lower() == Metadata.KEY_METADATA]
            return definitions.pop(matching_key[0], {}) if matching_key else {}
        return {}

    @property
    def metadata(self) -> dict:
        """Returns metadata dictionary or an empty dict if no metadata are defined."""
        return self._metadata

    @final
    def _extract_metadata(self, definitions: dict[str, Any] | None) -> None:
        """If keyword `metadata` is found on the highest level of given `definitions`, metadata are removed and set."""
        self._metadata = self.__extract_metadata(definitions)

    @final
    def get_metadata_string(self) -> str:
        """Returns string representation of metadata dictionary or empty string if no metadata are present."""
        return str(self._metadata) if self.has_metadata() else ""

    @final
    def has_metadata(self) -> bool:
        """Returns True if metadata are available."""
        return bool(self._metadata)

    @final
    def to_dict(self) -> dict:
        """Returns a dictionary representation of this item (using its _to_dict method) and adding its metadata."""
        child_data = self._to_dict()
        self.__enrich_with_metadata(child_data)
        return child_data

    @abstractmethod
    def _to_dict(self) -> dict:
        """Returns a dictionary representation of this item excluding its metadata."""

    @final
    def __enrich_with_metadata(self, data: dict) -> dict:
        """Returns data enriched with metadata field - if any metadata is available."""
        if self.has_metadata():
            data[self.KEY_METADATA] = self._metadata
        return data


class MetadataComponent(Metadata):
    """A component that can contain metadata and may be associated with other Objects.

    This can be attached to objects that cannot be derived from the Metadata class themselves.
    """

    def __init__(self, additional_definition: dict | None = None) -> None:
        super().__init__(additional_definition)

    def _to_dict(self) -> dict[str, dict]:
        return {}


class ValueContainer:
    """A container for values of any type with optional associated metadata."""

    class ParseError(InputError):
        """An error that occurred while parsing content for metadata-annotated simple values."""

    _ERR_VALUES_ILL_FORMATTED = "Only Lists or Dictionaries are supported for value definitions, but was: {}"

    def __init__(self, definition: dict[str, Any] | list | None = None) -> None:
        """Sets data (and metadata - if any) from given `definition`.

        Args:
            definition: dictionary representation of value(s) with potential associated metadata

        Raises:
            ParseError: if value definition is ill-formatted
        """
        self._values: dict[Any, MetadataComponent] = self._extract_values(definition)

    @staticmethod
    def _extract_values(definition: dict[str, Any] | list | None) -> dict[Any, MetadataComponent]:
        """Returns value data (and optional metadata) extracted from given `definition`.

        Args:
            definition: dictionary representation of value with potential associated metadata

        Returns:
            value linked with associated metadata (if any)

        Raises:
            ParseError: if value definition is ill-formatted, logged on level "ERROR"
        """
        if definition is None:
            return {}
        if isinstance(definition, dict):
            return {key: MetadataComponent(key_definition) for key, key_definition in definition.items()}
        if isinstance(definition, list):
            return {key: MetadataComponent() for key in definition}
        raise log_error(ValueContainer.ParseError(ValueContainer._ERR_VALUES_ILL_FORMATTED.format(repr(definition))))

    @property
    def values(self) -> dict[str, MetadataComponent]:
        """Returns stored values and each associated MetadataComponent."""
        return self._values

    def as_list(self) -> list[Any]:
        """Returns all values as list - excluding any metadata."""
        return list(self._values.keys())

    def to_dict(self) -> dict[Any, dict[str, dict]]:
        """Gives all values in dictionary representation.

        Returns:
            If metadata are present they are mapped to each value; values without metadata associate with an empty dict
        """
        return {value: component_metadata.to_dict() for value, component_metadata in self._values.items()}

    def has_value(self, to_search: Any) -> bool:
        """Returns True if given value `to_search` is a key in this ValueContainer.

        Args:
            to_search: value that is searched for in the keys of this ValueContainer

        Returns:
            True if value is found, False otherwise
        """
        return to_search in self._values.keys()

    def is_empty(self) -> bool:
        """Returns True if no values are stored herein.

        Returns:
            True if no values are stored in this container, False otherwise
        """
        return len(self._values) == 0
