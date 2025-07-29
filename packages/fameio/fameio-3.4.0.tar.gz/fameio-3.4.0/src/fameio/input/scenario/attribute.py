# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from enum import Enum, auto
from numbers import Number
from typing import Any, NamedTuple, Final

from fameio.input.metadata import Metadata, MetadataComponent
from fameio.tools import keys_to_lower
from .exception import log_scenario_error
from ...logs import log_error


class Attribute(Metadata):
    """An Attribute of an agent in a scenario."""

    KEY_VALUE: Final[str] = "Value".lower()
    KEY_VALUES: Final[str] = "Values".lower()

    NAME_STRING_SEPARATOR: Final[str] = "."

    class __ValueMeta(NamedTuple):
        """NamedTuple for a primitive value associated with Metadata."""

        value: str | Number
        meta: MetadataComponent

    class __NestedMeta(NamedTuple):
        """NamedTuple for a nested value associated with Metadata."""

        value: dict[str, Any]
        meta: MetadataComponent

    class __DefinitionType(Enum):
        """Indicates the type of data definition for an Attribute."""

        VALUE = auto()
        VALUE_LIST = auto()
        NESTED = auto()
        NESTED_LIST = auto()

    _ERR_CREATION = "Found error in specification of Attribute '{}'."
    _ERR_VALUE_MISSING = "Value not specified for Attribute '{}' - leave this Attribute out or specify a value."
    _ERR_LIST_EMPTY = "Attribute was assigned an empty list - please remove attribute or fill empty assignments."
    _ERR_DICT_EMPTY = "Attribute was assigned an empty dictionary - please remove or fill empty assignments."
    _ERR_MIXED_DATA = "Attribute was assigned a list with mixed complex and simple entries - please fix."

    def __init__(self, name: str, definitions: str | Number | list | dict) -> None:
        """Creates a new Attribute.

        Args:
            name: full name of the Attribute including the parent Attribute(s) names
            definitions: of this Attribute including its inner elements, if any

        Raises:
            ScenarioError: if this Attribute or its inner elements could not be created, logged with level "ERROR"
        """
        self._full_name = name
        if definitions is None:
            raise log_scenario_error(Attribute._ERR_VALUE_MISSING.format(name))
        super().__init__(definitions)
        try:
            data_type = Attribute._get_data_type(definitions)
        except ValueError as e:
            raise log_scenario_error(Attribute._ERR_CREATION.format(name)) from e

        self._value: str | Number | None = None
        self._value_list: list[Attribute.__ValueMeta] | None = None
        self._nested: dict[str, Attribute] | None = None
        self._nested_list: list[Attribute.__NestedMeta] | None = None

        if data_type is Attribute.__DefinitionType.VALUE:
            self._value = self._extract_value(definitions).value  # type: ignore[arg-type]
        elif data_type is Attribute.__DefinitionType.VALUE_LIST:
            self._value_list = self._extract_values(definitions)  # type: ignore[arg-type]
        elif data_type is Attribute.__DefinitionType.NESTED:
            self._nested = Attribute._build_attribute_dict(name, definitions)  # type: ignore[arg-type]
        elif data_type is Attribute.__DefinitionType.NESTED_LIST:
            self._nested_list = []
            values = keys_to_lower(definitions)[Attribute.KEY_VALUES] if isinstance(definitions, dict) else definitions
            for list_index, definition in enumerate(values):  # type: ignore[arg-type]
                list_meta = MetadataComponent(definition)
                list_extended_name = name + Attribute.NAME_STRING_SEPARATOR + str(list_index)
                nested_items = Attribute._build_attribute_dict(list_extended_name, definition)
                self._nested_list.append(Attribute.__NestedMeta(value=nested_items, meta=list_meta))

    @staticmethod
    def _get_data_type(definitions: Any) -> Attribute.__DefinitionType:
        """Returns type of data derived from given `definitions`.

        Args:
            definitions: to deduct the data type from

        Returns:
            data type derived from given definitions

        Raises:
            ValueError: if definitions are empty or could not be derived, logged with level "ERROR"
        """
        if isinstance(definitions, list):
            if len(definitions) == 0:
                raise log_error(ValueError(Attribute._ERR_LIST_EMPTY))
            return Attribute._get_data_type_list(definitions)
        if isinstance(definitions, dict):
            if len(definitions) == 0:
                raise log_error(ValueError(Attribute._ERR_DICT_EMPTY))
            return Attribute._get_data_type_dict(definitions)
        return Attribute.__DefinitionType.VALUE

    @staticmethod
    def _get_data_type_list(definitions: list[Any]) -> Attribute.__DefinitionType:
        """Returns type of data from a given non-empty list `definitions`.

        Args:
            definitions: list of data to derive data type from

        Returns:
            data type of data list

        Raises:
            ValueError: if definitions represent a mix of simple and complex entries, logged with level "ERROR"
        """
        if all(Attribute._is_value_definition(entry) for entry in definitions):
            return Attribute.__DefinitionType.VALUE_LIST
        if Attribute._is_list_of_dict(definitions):
            return Attribute.__DefinitionType.NESTED_LIST
        raise log_error(ValueError(Attribute._ERR_MIXED_DATA))

    @staticmethod
    def _is_list_of_dict(definitions: list) -> bool:
        """Returns True if given `definitions` is a list of (only) dict."""
        return all(isinstance(entry, dict) for entry in definitions)

    @staticmethod
    def _get_data_type_dict(definitions: dict[str, Any]) -> Attribute.__DefinitionType:
        """Returns type of data from a given non-empty dict `definitions`.

        Args:
            definitions: to derive the data type from

        Returns:
            data type derived from given `definitions`

        Raises:
            ValueError: if definitions represent a mix of simple and complex entries, logged with level "ERROR"
        """
        low_keys = keys_to_lower(definitions)
        if Attribute.KEY_VALUE in low_keys.keys():
            return Attribute.__DefinitionType.VALUE
        if Attribute.KEY_VALUES in low_keys.keys():
            values = low_keys[Attribute.KEY_VALUES]
            if all(Attribute._is_value_definition(entry) for entry in values):
                return Attribute.__DefinitionType.VALUE_LIST
            if Attribute._is_list_of_dict(values):
                return Attribute.__DefinitionType.NESTED_LIST
            raise log_error(ValueError(Attribute._ERR_MIXED_DATA))
        return Attribute.__DefinitionType.NESTED

    @staticmethod
    def _is_value_definition(definition: Any) -> bool:
        """Returns True if given `definition` is either a dict with a key `Value` or a simple value."""
        if isinstance(definition, dict):
            return Attribute.KEY_VALUE in keys_to_lower(definition).keys()
        return isinstance(definition, (str, Number))

    @staticmethod
    def _extract_value(definition: str | Number | dict[str, Any]) -> Attribute.__ValueMeta:
        """Creates a ValueMeta Tuple associating a Value with its optional metadata."""
        if isinstance(definition, dict):
            return Attribute.__ValueMeta(
                value=keys_to_lower(definition)[Attribute.KEY_VALUE], meta=MetadataComponent(definition)
            )
        return Attribute.__ValueMeta(value=definition, meta=MetadataComponent())

    @staticmethod
    def _extract_values(definition: list | dict) -> list[Attribute.__ValueMeta]:
        """Creates a list of ValueMeta Tuples, each associating a value with optional metadata."""
        values = keys_to_lower(definition)[Attribute.KEY_VALUES] if isinstance(definition, dict) else definition
        return [Attribute._extract_value(entry) for entry in values]

    @staticmethod
    def _build_attribute_dict(parent_name: str, definitions: dict[str, Any]) -> dict[str, Attribute]:
        """Returns a new dictionary containing Attributes generated from given `definitions`.

        Args:
            parent_name: name of parent element
            definitions: of the Attributes

        Returns:
            dictionary of Attributes created from given definitions

        Raises:
            ScenarioError: if any of the Attributes could not be created, logged with level "ERROR"
        """
        inner_elements = {}
        for nested_name, value in definitions.items():
            full_name = parent_name + Attribute.NAME_STRING_SEPARATOR + nested_name
            inner_elements[nested_name] = Attribute(full_name, value)
        return inner_elements

    @property
    def has_value(self) -> bool:
        """Returns True if Attribute has any value assigned."""
        return self._value is not None or self._value_list is not None

    @property
    def value(self) -> str | Number | list[str | Number] | None:
        """Returns value or list of values if available on this Attribute (ignoring any Metadata), else None."""
        if self._value is not None:
            return self._value
        if self._value_list is not None:
            return [item.value for item in self._value_list]
        return None

    @property
    def has_nested(self) -> bool:
        """Returns True if nested Attributes are present, False otherwise; also returns False for nested lists."""
        return self._nested is not None

    @property
    def nested(self) -> dict[str, Attribute]:
        """Returns dictionary of all nested Attributes if nested Attributes are present, else empty dict."""
        return self._nested if self._nested is not None else {}

    @property
    def has_nested_list(self) -> bool:
        """Returns True if list of nested items is present."""
        return self._nested_list is not None

    @property
    def nested_list(self) -> list[dict[str, Attribute]]:
        """Return list of all nested Attribute dictionaries if such are present, else an empty list."""
        return [entry.value for entry in self._nested_list] if self._nested_list is not None else []

    def __repr__(self) -> str:
        return self._full_name

    def _to_dict(self) -> dict[str, Any]:
        if self._value is not None:
            return {self.KEY_VALUE: self._value}
        if self._value_list is not None:
            return {
                self.KEY_VALUES: [{self.KEY_VALUE: entry.value, **entry.meta.to_dict()} for entry in self._value_list]
            }
        if self._nested is not None:
            return {name: attribute.to_dict() for name, attribute in self.nested.items()}
        if self._nested_list is not None:
            return {
                self.KEY_VALUES: [
                    {**{name: attribute.to_dict() for name, attribute in entry.value.items()}, **entry.meta.to_dict()}
                    for entry in self._nested_list
                ]
            }
        return {}
