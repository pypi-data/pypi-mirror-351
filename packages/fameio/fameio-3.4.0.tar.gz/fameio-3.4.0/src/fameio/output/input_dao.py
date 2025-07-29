# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import ast
from typing import Any

from fameprotobuf.data_storage_pb2 import DataStorage
from fameprotobuf.field_pb2 import NestedField
from fameprotobuf.input_file_pb2 import InputData

from fameio.input.scenario import GeneralProperties, Agent, Contract, Scenario
from fameio.input.schema import Schema, AttributeSpecs, AttributeType
from fameio.logs import log_error
from fameio.output import OutputError
from fameio.series import TimeSeriesManager, TimeSeriesError


class InputConversionError(OutputError):
    """Indicates an error during reconstruction of input from its protobuf representation."""


class InputDao:
    """Data access object for inputs saved in protobuf."""

    _ERR_NO_INPUTS = "No input data found on file."
    _ERR_MULTIPLE_INPUTS = "File corrupt. More than one input section found on file."
    _ERR_NO_SCHEMA = "No schema found on file - cannot recover inputs."
    _ERR_SERIES_MISSING = "References time series '{}' was not registered on file."

    _FIELD_NAME_MAP: dict = {
        AttributeType.STRING: "string_values",
        AttributeType.STRING_SET: "string_values",
        AttributeType.ENUM: "string_values",
        AttributeType.INTEGER: "int_values",
        AttributeType.DOUBLE: "double_values",
        AttributeType.LONG: "long_values",
        AttributeType.TIME_STAMP: "long_values",
        AttributeType.TIME_SERIES: "series_id",
        AttributeType.BLOCK: "fields",
    }

    def __init__(self) -> None:
        self._inputs: list[InputData] = []
        self._timeseries_manager: TimeSeriesManager = TimeSeriesManager()

    def store_inputs(self, data_storages: list[DataStorage]) -> None:
        """Extracts and stores Inputs in given DataStorages - if such are present.

        Args:
            data_storages: to be scanned for InputData
        """
        self._inputs.extend([data_storage.input for data_storage in data_storages if data_storage.HasField("input")])

    def recover_inputs(self) -> tuple[TimeSeriesManager, Scenario]:
        """Recovers inputs to GeneralProperties, Schema, Agents, Contracts, Timeseries.

        Return:
            recovered timeseries and scenario

        Raises:
            InputConversionError: if inputs could not be recovered, logged with level "ERROR"
            InputError: if scenario in file is incompatible with this version of fameio, logged with level "ERROR"
        """
        input_data = self._get_input_data()
        schema = self._get_schema(input_data)
        scenario = Scenario(schema, self._get_general_properties(input_data))
        for contract in self._get_contracts(input_data):
            scenario.add_contract(contract)

        self._init_timeseries(input_data)
        for agent in self._get_agents(input_data, schema):
            scenario.add_agent(agent)

        return self._timeseries_manager, scenario

    def _get_input_data(self) -> InputData:
        """Check that exactly one previously extracted input data exist, otherwise raises an exception.

        Returns:
            the previously extracted input data

        Raises:
            InputConversionException: if no input, or more than one input is present, logged with level "ERROR"
        """
        if not self._inputs:
            raise log_error(InputConversionError(self._ERR_NO_INPUTS))
        if len(self._inputs) > 1:
            raise log_error(InputConversionError(self._ERR_MULTIPLE_INPUTS))
        return self._inputs[0]

    @staticmethod
    def _get_schema(input_data: InputData) -> Schema:
        """Read and return Schema from given `input_data`."""
        return Schema.from_string(input_data.schema)

    @staticmethod
    def _get_general_properties(input_data: InputData) -> GeneralProperties:
        """Read and return GeneralProperties from given `input_data`."""
        return GeneralProperties(
            run_id=input_data.run_id,
            simulation_start_time=input_data.simulation.start_time,
            simulation_stop_time=input_data.simulation.stop_time,
            simulation_random_seed=input_data.simulation.random_seed,
        )

    @staticmethod
    def _get_contracts(input_data: InputData) -> list[Contract]:
        """Read and return Contracts from given `input_data`."""
        return [
            Contract(
                sender_id=contract.sender_id,
                receiver_id=contract.receiver_id,
                product_name=contract.product_name,
                delivery_interval=contract.delivery_interval_in_steps,
                first_delivery_time=contract.first_delivery_time,
                expiration_time=contract.expiration_time,
                metadata=ast.literal_eval(contract.metadata) if contract.metadata else None,
            )
            for contract in input_data.contracts
        ]

    def _init_timeseries(self, input_data: InputData) -> None:
        """Read timeseries from given `input_data` and initialise TimeSeriesManager."""
        self._timeseries_manager.reconstruct_time_series(list(input_data.time_series))

    def _get_agents(self, input_data: InputData, schema: Schema) -> list[Agent]:
        """Read and return Agents from given `input_data`.

        Args:
            input_data: to read agents from
            schema: corresponding to the agent definitions

        Returns:
            all extracted agents

        Raises:
            InputError: if agents cannot be reconstructed, logged with level "ERROR"
            InputConversionError: if attributes could not be reconstructed, logged with level "ERROR"
        """
        agents = []
        for agent_dao in input_data.agents:
            agent = Agent(
                agent_id=agent_dao.id,
                type_name=agent_dao.class_name,
                metadata=ast.literal_eval(agent_dao.metadata) if agent_dao.metadata else None,
            )
            attribute_dict = self._get_attributes(
                list(agent_dao.fields), schema.agent_types[agent_dao.class_name].attributes
            )
            agent.init_attributes_from_dict(attribute_dict)
            agents.append(agent)
        return agents

    def _get_attributes(self, fields: list[NestedField], schematics: dict[str, AttributeSpecs]) -> dict[str, Any]:
        """Read and return all Attributes as Dictionary from given list of fields.

        Args:
            fields: data fields representing attributes
            schematics: description of the attributes associated by name

        Returns:
            all recovered attributes and their associated values

        Raises:
            InputConversionError: if attributes could not be reconstructed, logged with level "ERROR"
        """
        attributes: dict[str, Any] = {}
        for field in fields:
            attributes[field.field_name] = self._get_field_value(field, schematics[field.field_name])
        return attributes

    def _get_field_value(self, field: NestedField, schematic: AttributeSpecs) -> Any:
        """Extracts and returns value(s) of given `field`.

        Args:
            field: to extract the value(s) from
            schematic: describing the data type of this field

        Returns:
            value(s) of provided field

        Raises:
            InputConversionError: if TimeSeries could not be found, logged with level "ERROR"
        """
        attribute_type: AttributeType = schematic.attr_type
        if attribute_type is AttributeType.TIME_SERIES:
            try:
                return self._timeseries_manager.get_reconstructed_series_by_id(field.series_id)
            except TimeSeriesError as e:
                raise log_error(InputConversionError(self._ERR_SERIES_MISSING.format(field.series_id))) from e
        if attribute_type is AttributeType.BLOCK:
            if schematic.is_list:
                return [self._get_attributes(list(entry.fields), schematic.nested_attributes) for entry in field.fields]
            return self._get_attributes(list(field.fields), schematic.nested_attributes)
        value = getattr(field, self._FIELD_NAME_MAP[attribute_type])
        if schematic.is_list:
            return list(value)
        return list(value)[0]
