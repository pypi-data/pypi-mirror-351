# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any, Final

from fameio.input import InputError, SchemaError
from fameio.input.metadata import Metadata, MetadataComponent, ValueContainer
from fameio.logs import log, log_error
from fameio.tools import keys_to_lower
from .attribute import AttributeSpecs


class AgentType(Metadata):
    """Schema definitions for an Agent type."""

    KEY_ATTRIBUTES: Final[str] = "Attributes".lower()
    KEY_PRODUCTS: Final[str] = "Products".lower()
    KEY_OUTPUTS: Final[str] = "Outputs".lower()

    _ERR_NAME_INVALID = "'{}' is not a valid name for AgentTypes"
    _ERR_NO_STRING = "{} definition of AgentType '{}' contains keys other than string: '{}'"
    _ERR_UNKNOWN_STRUCTURE = "{} definition of AgentType '{}' is neither list nor dictionary: '{}'"

    _NO_ATTRIBUTES = "Agent '{}' has no specified 'Attributes'."
    _NO_PRODUCTS = "Agent '{}' has no specified 'Products'."
    _NO_OUTPUTS = "Agent '{}' has no specified 'Outputs'."

    def __init__(self, name: str):
        """
        Initialise a new AgentType

        Args:
            name: name of the AgenType

        Raises:
            SchemaError: if name is None, empty, or only whitespaces, logged with level "ERROR"
        """
        super().__init__()
        if not name or name.isspace():
            raise log_error(SchemaError(AgentType._ERR_NAME_INVALID.format(name)))
        self._name = name
        self._attributes: dict[str, AttributeSpecs] = {}
        self._products: ValueContainer = ValueContainer()
        self._outputs: ValueContainer = ValueContainer()

    @classmethod
    def from_dict(cls, name: str, definitions: dict) -> AgentType:
        """Creates AgentType with given `name` from specified dictionary.

        Args:
            name: of the agent type
            definitions: of the agent type specifying, e.g., its attributes and products

        Returns:
            a new instance of AgentType

        Raises:
            SchemaError: if definitions are invalid, logged with level "ERROR"
        """
        agent_type = cls(name)
        agent_type._extract_metadata(definitions)

        definition = keys_to_lower(definitions)
        if AgentType.KEY_ATTRIBUTES in definition:
            for attribute_name, attribute_details in definition[AgentType.KEY_ATTRIBUTES].items():
                full_name = name + "." + attribute_name
                agent_type._attributes[attribute_name] = AttributeSpecs(full_name, attribute_details)
        else:
            log().info(AgentType._NO_ATTRIBUTES.format(name))

        if AgentType.KEY_PRODUCTS in definition and definition[AgentType.KEY_PRODUCTS]:
            agent_type._products = AgentType._read_values(
                section="Products", agent_type=name, values=definition[AgentType.KEY_PRODUCTS]
            )
        else:
            log().info(AgentType._NO_PRODUCTS.format(name))

        if AgentType.KEY_OUTPUTS in definition and definition[AgentType.KEY_OUTPUTS]:
            agent_type._outputs = AgentType._read_values(
                section="Outputs", agent_type=name, values=definition[AgentType.KEY_OUTPUTS]
            )
        else:
            log().debug(AgentType._NO_OUTPUTS.format(name))

        return agent_type

    @staticmethod
    def _read_values(section: str, agent_type: str, values: Any) -> ValueContainer:
        """Returns ValueContainer for `section` in specifications of `agent_type` extracted from given `values`.

        Args:
            section: key of the section that contains the values
            agent_type: name of the agent type that the values are associated with
            values: list or dict with value definitions

        Returns:
            container for all the extracted values

        Raises:
            SchemaError: if the values are ill-formatted, logged with level "ERROR"
        """
        try:
            data = ValueContainer(values)
        except InputError as e:
            raise log_error(SchemaError(AgentType._ERR_UNKNOWN_STRUCTURE.format(section, agent_type, values))) from e
        if not all(isinstance(item, str) for item in data.as_list()):
            raise log_error(SchemaError(AgentType._ERR_NO_STRING.format(section, agent_type, data.as_list())))
        return data

    @property
    def name(self) -> str:
        """Returns the agent type name."""
        return self._name

    @property
    def products(self) -> dict[str, MetadataComponent]:
        """Returns dict of products or an empty dict if no products are defined."""
        return self._products.values

    def get_product_names(self) -> list[str]:
        """Returns list of product names or an empty list if no products are defined."""
        return self._products.as_list()

    @property
    def attributes(self) -> dict[str, AttributeSpecs]:
        """Returns list of Attributes of this agent or an empty list if no attributes are defined."""
        return self._attributes

    @property
    def outputs(self) -> dict[str, MetadataComponent]:
        """Returns list of outputs or an empty list if no outputs are defined."""
        return self._outputs.values

    def _to_dict(self) -> dict:
        return {
            self.KEY_ATTRIBUTES: {name: attribute.to_dict() for name, attribute in self._attributes.items()},
            self.KEY_PRODUCTS: self._products.to_dict(),
            self.KEY_OUTPUTS: self._outputs.to_dict(),
        }
