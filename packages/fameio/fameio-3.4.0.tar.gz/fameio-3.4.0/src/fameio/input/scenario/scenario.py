# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Final, Any

from fameio.input import SchemaError
from fameio.input.metadata import Metadata
from fameio.input.scenario.agent import Agent
from fameio.input.scenario.contract import Contract
from fameio.input.scenario.exception import get_or_raise, log_scenario_error
from fameio.input.scenario.fameiofactory import FameIOFactory
from fameio.input.scenario.generalproperties import GeneralProperties
from fameio.input.scenario.stringset import StringSet
from fameio.input.schema import Schema
from fameio.tools import keys_to_lower


class Scenario(Metadata):
    """Definition of a scenario."""

    KEY_SCHEMA: Final[str] = "Schema".lower()
    KEY_GENERAL: Final[str] = "GeneralProperties".lower()
    KEY_AGENTS: Final[str] = "Agents".lower()
    KEY_CONTRACTS: Final[str] = "Contracts".lower()
    KEY_STRING_SETS: Final[str] = "StringSets".lower()

    _MISSING_KEY = "Scenario definition misses required key '{}'."
    _ERR_SCHEMA = "Could not create scenario: Definition of Schema has errors."
    _ERR_STRING_SET = "Could not create scenario: Definition of StringSet '{}' has errors."
    _ERR_MULTI_CONTRACT = "Could not create scenario: Definition of Contracts has errors: {}"
    _ERR_CONTRACT = "Could not create scenario: Definition of Contract has errors: {}"

    def __init__(self, schema: Schema, general_props: GeneralProperties) -> None:
        super().__init__()
        self._schema = schema
        self._general_props = general_props
        self._string_sets: dict[str, StringSet] = {}
        self._agents: list[Agent] = []
        self._contracts: list[Contract] = []

    @classmethod
    def from_dict(cls, definitions: dict, factory: FameIOFactory = FameIOFactory()) -> Scenario:
        """Parses scenario from provided `definitions` using given `factory`.

        Args:
            definitions: dictionary representation of scenario
            factory: helper class with static helpers to instantiate scenario components

        Returns:
            new Scenario

        Raises:
            ScenarioError: if scenario definitions are incomplete or erroneous, logged with level "ERROR"
        """
        definitions = keys_to_lower(definitions)

        schema = Scenario._extract_schema(definitions, factory)
        general_properties_definition = get_or_raise(definitions, Scenario.KEY_GENERAL, Scenario._MISSING_KEY)
        general_properties = factory.new_general_properties_from_dict(general_properties_definition)
        scenario = cls(schema, general_properties)
        scenario._extract_metadata(definitions)

        scenario._string_sets = Scenario._extract_string_sets(definitions, factory)
        scenario._agents = [
            factory.new_agent_from_dict(agent_definition)
            for agent_definition in definitions.get(Scenario.KEY_AGENTS, [])
        ]
        scenario._contracts = Scenario._extract_contracts(definitions, factory)
        return scenario

    @staticmethod
    def _extract_schema(definitions: dict, factory: FameIOFactory) -> Schema:
        """Extracts schema from given definitions and creates Schema from it.

        Args:
            definitions: dictionary representation of scenario
            factory: helper class with static helpers to instantiate scenario components

        Returns:
            new schema

        Raises:
            ScenarioError: if schema definitions are missing, incomplete, or erroneous; logged on level "ERROR"
        """
        schema_definition = get_or_raise(definitions, Scenario.KEY_SCHEMA, Scenario._MISSING_KEY)
        try:
            return factory.new_schema_from_dict(schema_definition)
        except SchemaError as e:
            raise log_scenario_error(Scenario._ERR_SCHEMA) from e

    @staticmethod
    def _extract_string_sets(definitions: dict, factory: FameIOFactory) -> dict[str, StringSet]:
        """Extracts string sets from given definitions and creates dictionary from it.

        Args:
            definitions: dictionary representation of scenario
            factory: helper class with static helpers to instantiate scenario components

        Returns:
            dictionary of string set names associated with their corresponding string set

        Raises:
            ScenarioError: if string set definitions are incomplete or erroneous; logged on level "ERROR"
        """
        string_sets = {}
        for name, string_set_definition in definitions.get(Scenario.KEY_STRING_SETS, {}).items():
            try:
                string_sets[name] = factory.new_string_set_from_dict(string_set_definition)
            except StringSet.StringSetError as e:
                raise log_scenario_error(Scenario._ERR_STRING_SET.format(name)) from e
        return string_sets

    @staticmethod
    def _extract_contracts(definitions: dict, factory: FameIOFactory) -> list[Contract]:
        """Extracts contracts from given definitions.

        Args:
            definitions: dictionary representation of scenario
            factory: helper class with static helpers to instantiate scenario components

        Returns:
            list of all created one-to-one contracts

        Raises:
            ScenarioError: if contract definitions are incomplete or erroneous; logged on level "ERROR"
        """
        contracts = []
        for multi_contract_definition in definitions.get(Scenario.KEY_CONTRACTS, []):
            try:
                for single_contract_definition in Contract.split_contract_definitions(multi_contract_definition):
                    try:
                        contracts.append(factory.new_contract_from_dict(single_contract_definition))
                    except Contract.ContractError as e:
                        raise log_scenario_error(Scenario._ERR_CONTRACT.format(single_contract_definition)) from e
            except Contract.ContractError as e:
                raise log_scenario_error(Scenario._ERR_MULTI_CONTRACT.format(multi_contract_definition)) from e
        return contracts

    def _to_dict(self) -> dict:
        """Serializes the scenario content to a dict."""
        result: dict[str, Any] = {
            Scenario.KEY_GENERAL: self.general_properties.to_dict(),
            Scenario.KEY_SCHEMA: self.schema.to_dict(),
        }
        if self.string_sets:
            result[Scenario.KEY_STRING_SETS] = {
                name: string_set.to_dict() for name, string_set in self.string_sets.items()
            }
        if self.agents:
            result[Scenario.KEY_AGENTS] = []
            for agent in self.agents:
                result[Scenario.KEY_AGENTS].append(agent.to_dict())
        if self.contracts:
            result[Scenario.KEY_CONTRACTS] = []
            for contract in self.contracts:
                result[Scenario.KEY_CONTRACTS].append(contract.to_dict())
        return result

    @property
    def agents(self) -> list[Agent]:
        """Returns all the agents of this scenario as a list."""
        return self._agents

    def add_agent(self, agent: Agent) -> None:
        """Adds a new agent to this scenario."""
        self._agents.append(agent)

    @property
    def contracts(self) -> list[Contract]:
        """Returns all the contracts of this scenario as a list."""
        return self._contracts

    def add_contract(self, contract: Contract) -> None:
        """Adds a new contract to this scenario."""
        self._contracts.append(contract)

    @property
    def schema(self) -> Schema:
        """Returns Schema associated with this scenario."""
        return self._schema

    @property
    def general_properties(self) -> GeneralProperties:
        """Returns General properties of this scenario."""
        return self._general_props

    @property
    def string_sets(self) -> dict[str, StringSet]:
        """Returns StringSets of this scenario."""
        return self._string_sets

    def add_string_set(self, name: str, string_set: StringSet) -> None:
        """Adds `string_set` with `name`."""
        self._string_sets[name] = string_set
