# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from fameio.input.schema import Schema
from .agent import Agent
from .contract import Contract
from .generalproperties import GeneralProperties
from .stringset import StringSet


class FameIOFactory:
    """Factory used to instantiate the types defined in a scenario file.

    This allows a client to subclass some types in order to extend what a scenario can contain.
    """

    @staticmethod
    def new_schema_from_dict(definitions: dict) -> Schema:
        """Loads given dictionary `definitions` into a new schema.

        Args:
            definitions: dictionary representation of schema

        Returns:
            new Schema

        Raises:
            SchemaError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        return Schema.from_dict(definitions)

    @staticmethod
    def new_general_properties_from_dict(definitions: dict) -> GeneralProperties:
        """Parses general properties from provided `definitions`.

        Args:
            definitions: dictionary representation of general properties

        Returns:
            new GeneralProperties

        Raises:
            ScenarioError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        return GeneralProperties.from_dict(definitions)

    @staticmethod
    def new_agent_from_dict(definitions: dict) -> Agent:
        """Parses an agent from provided `definitions`.

        Args:
            definitions: dictionary representation of an agent

        Returns:
            new agent

        Raises:
            ScenarioError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        return Agent.from_dict(definitions)

    @staticmethod
    def new_contract_from_dict(definitions: dict) -> Contract:
        """Parses contract from given `definitions`.

        Args:
            definitions: dictionary representation of a contract

        Returns:
            new contract

        Raises:
            ContractError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        return Contract.from_dict(definitions)

    @staticmethod
    def new_string_set_from_dict(definition: StringSet.StringSetType) -> StringSet:
        """Returns string set initialised from `definition`.

        Args:
            definition: dictionary representation of string set

        Returns:
            new string set

        Raises:
            StringSetError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        return StringSet.from_dict(definition)
