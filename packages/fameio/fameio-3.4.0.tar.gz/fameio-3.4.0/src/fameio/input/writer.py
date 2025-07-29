# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path
from typing import Any

from fameprotobuf.contract_pb2 import ProtoContract
from fameprotobuf.data_storage_pb2 import DataStorage
from fameprotobuf.execution_data_pb2 import ExecutionData
from fameprotobuf.field_pb2 import NestedField
from fameprotobuf.input_file_pb2 import InputData
from fameprotobuf.model_pb2 import ModelData
from google.protobuf.message import EncodeError

import fameio
from fameio.input import InputError
from fameio.input.scenario import Agent, Attribute, Contract, GeneralProperties, Scenario, StringSet
from fameio.input.schema import AttributeSpecs, AttributeType, JavaPackages, Schema
from fameio.logs import log, log_error
from fameio.output.reader import Reader
from fameio.series import TimeSeriesManager
from fameio.time import FameTime
from fameio.tools import ensure_is_list


class ProtoWriterError(InputError):
    """Indicates an error during writing of a protobuf file."""


class ProtoWriter:
    """Writes a given scenario to protobuf file."""

    _FAME_PROTOBUF_STREAM_HEADER = fameio.FILE_HEADER_V2

    _TYPE_NOT_IMPLEMENTED = "Protobuf representation for AttributeType '{}' not implemented."
    _CONTRACT_UNSUPPORTED = (
        "Unsupported value for Contract Attribute '{}'; "
        "Only support `int`, `float`, `enum` or `dict` types are supported here."
    )
    _USING_DEFAULT = "Using provided Default for Attribute: '{}'."
    _ERR_FILE_PATH = "Could not open file '{}' for writing. Please specify a valid output file."
    _ERR_PROTOBUF_ENCODING = "Could not encode to protobuf. Please contact FAME-Io developers: fame@dlr.de"
    _ERR_FILE_WRITE = "Could not write to file '{}'."

    _INFO_WRITING = "Writing scenario to protobuf file `{}`"
    _INFO_WRITING_COMPLETED = "Saved protobuf file `{}` to disk"

    def __init__(self, file_path: Path, time_series_manager: TimeSeriesManager) -> None:
        self.file_path: Path = file_path
        self._time_series_manager: TimeSeriesManager = time_series_manager

    def write_validated_scenario(self, scenario: Scenario) -> None:
        """Writes given validated Scenario to file.

        Args:
            scenario: to be written to file

        Raises:
            ProtoWriterError: if scenario could not be written to file, logged with level "ERROR"
        """
        data_storage = self._create_protobuf_from_scenario(scenario)
        serialised = self._serialise(data_storage)
        self._write_data_to_disk(serialised)

    def _create_protobuf_from_scenario(self, scenario: Scenario) -> DataStorage:
        """Returns given `scenario` written to new DataStorage protobuf.

        Args:
            scenario: to be converted to protobuf

        Returns:
            protobuf container with the scenario

        Raises:
            ProtoWriterError: if the protobuf representation cannot be constructed, logged with level "ERROR"
        """
        log().info("Converting scenario to protobuf.")
        pb_data_storage = DataStorage()
        pb_input = pb_data_storage.input

        self._set_general_properties(pb_input, scenario.general_properties)
        self._add_agents(pb_input, scenario.agents, scenario.schema)
        self._add_contracts(pb_input, scenario.contracts)
        self._set_time_series(pb_input)
        self._set_schema(pb_input, scenario.schema)
        self._set_string_sets(pb_input, scenario.string_sets)

        self._set_java_package_names(pb_data_storage.model, scenario.schema.packages)
        self._set_execution_versions(pb_data_storage.execution.version_data)
        return pb_data_storage

    @staticmethod
    def _set_general_properties(pb_input: InputData, general_properties: GeneralProperties) -> None:
        """Saves a scenario's general properties to specified protobuf `pb_input` container."""
        log().info("Adding General Properties")
        pb_input.run_id = general_properties.run_id
        pb_input.simulation.start_time = general_properties.simulation_start_time
        pb_input.simulation.stop_time = general_properties.simulation_stop_time
        pb_input.simulation.random_seed = general_properties.simulation_random_seed

    def _add_agents(self, pb_input: InputData, agents: list[Agent], schema: Schema) -> None:
        """Triggers setting of `agents` to `pb_input`.

        Args:
            pb_input: parent element to add the agents to
            agents: to be added to parent input
            schema: describing the agents' attributes

        Raises:
            ProtoWriterError: if any agent's attributes cannot be set, logged with level "ERROR"
        """
        log().info("Adding Agents")
        for agent in agents:
            pb_agent = self._set_agent(pb_input.agents.add(), agent)
            attribute_specs = schema.agent_types[agent.type_name].attributes
            self._set_attributes(pb_agent, agent.attributes, attribute_specs)
            pb_agent.metadata = agent.get_metadata_string()

    @staticmethod
    def _set_agent(pb_agent: InputData.AgentDao, agent: Agent) -> InputData.AgentDao:
        """Saves type and id of given `agent` to protobuf `pb_agent` container. Returns given `pb_agent`."""
        pb_agent.class_name = agent.type_name
        pb_agent.id = agent.id
        return pb_agent

    def _set_attributes(
        self,
        pb_parent: InputData.AgentDao | NestedField,
        attributes: dict[str, Attribute],
        specs: dict[str, AttributeSpecs],
    ) -> None:
        """Assigns `attributes` to protobuf fields of given `pb_parent` - cascades for nested Attributes.

        Args:
            pb_parent: to store the attributes in
            attributes: to be stored
            specs: attribute specifications associated with attributes

        Raises:
            ProtoWriterError: if any attribute cannot be set, logged with level "ERROR"
        """
        values_not_set = list(specs.keys())
        for name, attribute in attributes.items():
            pb_field = self._add_field(pb_parent, name)
            attribute_specs = specs[name]
            values_not_set.remove(name)
            attribute_type = attribute_specs.attr_type
            if attribute_type is AttributeType.BLOCK:
                if attribute_specs.is_list:
                    for index, entry in enumerate(attribute.nested_list):
                        pb_inner = self._add_field(pb_field, str(index))
                        self._set_attributes(pb_inner, entry, attribute_specs.nested_attributes)
                else:
                    self._set_attributes(pb_field, attribute.nested, attribute_specs.nested_attributes)
            else:
                self._set_attribute(pb_field, attribute.value, attribute_type)
        for name in values_not_set:
            attribute_specs = specs[name]
            if attribute_specs.is_mandatory:
                pb_field = self._add_field(pb_parent, name)
                self._set_attribute(pb_field, attribute_specs.default_value, attribute_specs.attr_type)
                log().info(self._USING_DEFAULT.format(name))

    @staticmethod
    def _add_field(pb_parent: InputData.AgentDao | NestedField, name: str) -> NestedField:
        """Returns new field with given `name` that is added to given `pb_parent`."""
        pb_field = pb_parent.fields.add()
        pb_field.field_name = name
        return pb_field

    def _set_attribute(self, pb_field: NestedField, value: Any, attribute_type: AttributeType) -> None:
        """Sets given `value` to given protobuf `pb_field` depending on specified `attribute_type`.

        Args:
            pb_field: parent element to contain the attribute value therein
            value: of the attribute
            attribute_type: type of the attribute

        Raises:
            ProtoWriterError: if the attribute type has no serialisation implementation, logged with level "ERROR"
        """
        if attribute_type is AttributeType.INTEGER:
            pb_field.int_values.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.DOUBLE:
            pb_field.double_values.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.LONG:
            pb_field.long_values.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.TIME_STAMP:
            pb_field.long_values.extend(ensure_is_list(FameTime.convert_string_if_is_datetime(value)))
        elif attribute_type in (AttributeType.ENUM, AttributeType.STRING, AttributeType.STRING_SET):
            pb_field.string_values.extend(ensure_is_list(value))
        elif attribute_type is AttributeType.TIME_SERIES:
            pb_field.series_id = self._time_series_manager.get_series_id_by_identifier(value)
        else:
            raise log_error(ProtoWriterError(self._TYPE_NOT_IMPLEMENTED.format(attribute_type)))

    @staticmethod
    def _add_contracts(pb_input: InputData, contracts: list[Contract]) -> None:
        """Adds given contracts to input data.

        Args:
            pb_input: parent element to have the contracts added to
            contracts: to be added

        Raises:
            ProtoWriterError: if any contract cannot be added, logged with level "ERROR"
        """
        log().info("Adding Contracts")
        for contract in contracts:
            pb_contract = ProtoWriter._set_contract(pb_input.contracts.add(), contract)
            ProtoWriter._set_contract_attributes(pb_contract, contract.attributes)
            pb_contract.metadata = contract.get_metadata_string()

    @staticmethod
    def _set_contract(pb_contract: ProtoContract, contract: Contract) -> ProtoContract:
        """Saves given `contract` details to protobuf container `pb_contract`. Returns given `pb_contract`."""
        pb_contract.sender_id = contract.sender_id
        pb_contract.receiver_id = contract.receiver_id
        pb_contract.product_name = contract.product_name
        pb_contract.first_delivery_time = contract.first_delivery_time
        pb_contract.delivery_interval_in_steps = contract.delivery_interval
        if contract.expiration_time:
            pb_contract.expiration_time = contract.expiration_time
        return pb_contract

    @staticmethod
    def _set_contract_attributes(pb_parent: ProtoContract | NestedField, attributes: dict[str, Attribute]) -> None:
        """Assign (nested) Attributes to given protobuf container `pb_parent`.

        Args:
            pb_parent: parent element, either a contract or an attribute
            attributes: to be set as child elements of parent

        Raises:
            ProtoWriterError: if a type unsupported for contract attributes is found, logged with level "ERROR"
        """
        for name, attribute in attributes.items():
            log().debug(f"Assigning contract attribute `{name}`.")
            pb_field = ProtoWriter._add_field(pb_parent, name)

            if attribute.has_value:
                value = attribute.value
                if isinstance(value, int):
                    pb_field.int_values.extend([value])
                elif isinstance(value, float):
                    pb_field.double_values.extend([value])
                elif isinstance(value, str):
                    pb_field.string_values.extend([value])
                else:
                    raise log_error(ProtoWriterError(ProtoWriter._CONTRACT_UNSUPPORTED.format(str(attribute))))
            elif attribute.has_nested:
                ProtoWriter._set_contract_attributes(pb_field, attribute.nested)

    def _set_time_series(self, pb_input: InputData) -> None:
        """Adds all time series from TimeSeriesManager to given `pb_input`."""
        log().info("Adding TimeSeries")
        for unique_id, identifier, data in self._time_series_manager.get_all_series():
            pb_series = pb_input.time_series.add()
            pb_series.series_id = unique_id
            pb_series.series_name = identifier
            pb_series.time_steps.extend(list(data[0]))
            pb_series.values.extend(list(data[1]))

    @staticmethod
    def _set_schema(pb_input: InputData, schema: Schema) -> None:
        """Sets the given `schema` `pb_input`."""
        log().info("Adding Schema")
        pb_input.schema = schema.to_string()

    @staticmethod
    def _set_string_sets(pb_input: InputData, string_sets: dict[str, StringSet]) -> None:
        """Adds the given StringSets to given `pb_input`."""
        for name, string_set in string_sets.items():
            pb_set = pb_input.string_sets.add()
            pb_set.name = name
            for value, specification in string_set.values.items():
                pb_value = pb_set.values.add()
                pb_value.name = value
                if specification.has_metadata():
                    pb_value.metadata = specification.get_metadata_string()
            if string_set.has_metadata():
                pb_set.metadata = string_set.get_metadata_string()

    @staticmethod
    def _set_java_package_names(pb_model: ModelData, java_packages: JavaPackages) -> None:
        """Adds given JavaPackages names to given ModelData section."""
        pb_packages = pb_model.package_definition
        pb_packages.agents.extend(java_packages.agents)
        pb_packages.data_items.extend(java_packages.data_items)
        pb_packages.portables.extend(java_packages.portables)

    @staticmethod
    def _set_execution_versions(pb_version_data: ExecutionData.VersionData) -> None:
        """Adds version strings for fameio, fameprotobuf, and python to the given Versions message."""
        pb_version_data.fame_protobuf = metadata.version("fameprotobuf")
        pb_version_data.fame_io = metadata.version("fameio")
        pb_version_data.python = sys.version

    def _serialise(self, data_storage: DataStorage) -> bytes:
        """Serialise given data storage to bytes.

        Args:
            data_storage: to be serialised

        Returns:
            binary string representation of given data storage

        Raises:
            ProtoWriterError: if given data storage could not be serialised, logged with level "ERROR"
        """
        try:
            return data_storage.SerializeToString()
        except EncodeError as e:
            raise log_error(ProtoWriterError(self._ERR_PROTOBUF_ENCODING)) from e

    def _write_data_to_disk(self, serialised_data: bytes) -> None:
        """Writes given serialised data to file.

        Args:
            serialised_data: to be written to file

        Raises:
            ProtoWriterError: if file could not be opened or written, logged with level "ERROR"
        """
        log().info(self._INFO_WRITING.format(self.file_path))
        try:
            with open(self.file_path, "wb") as file:
                try:
                    file.write(self._FAME_PROTOBUF_STREAM_HEADER.encode(Reader.HEADER_ENCODING))
                    file.write(len(serialised_data).to_bytes(Reader.BYTES_DEFINING_MESSAGE_LENGTH, byteorder="big"))
                    file.write(serialised_data)
                except IOError as e:
                    raise log_error(ProtoWriterError(self._ERR_FILE_WRITE.format(self.file_path))) from e
        except OSError as e:
            raise log_error(ProtoWriterError(ProtoWriter._ERR_FILE_PATH.format(self.file_path), e)) from e
        log().info(self._INFO_WRITING_COMPLETED.format(self.file_path))
