#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd

from fameio.cli import update_default_config
from fameio.cli.convert_results import handle_args, CLI_DEFAULTS as DEFAULT_CONFIG
from fameio.cli.options import Options
from fameio.input import InputError
from fameio.logs import fameio_logger, log, log_error, log_critical
from fameio.output import OutputError
from fameio.output.agent_type import AgentTypeLog
from fameio.output.conversion import apply_time_option, apply_time_merging
from fameio.output.csv_writer import CsvWriter
from fameio.output.data_transformer import DataTransformer, INDEX
from fameio.output.execution_dao import ExecutionDao
from fameio.output.input_dao import InputDao
from fameio.output.output_dao import OutputDAO
from fameio.output.reader import Reader
from fameio.output.yaml_writer import data_to_yaml_file
from fameio.scripts.exception import ScriptError

_ERR_OUT_OF_MEMORY = "Out of memory. Retry result conversion using `-m` or `--memory-saving` option."
_ERR_MEMORY_SEVERE = "Out of memory despite memory-saving mode. Reduce output interval in `FAME-Core` and rerun model."
_ERR_FILE_OPEN_FAIL = "Could not open file: '{}'"
_ERR_RECOVER_INPUT = "Input recovery failed: File was created with `fameio=={}`. Use that version to recover inputs."
_ERR_FAIL = "Results conversion script failed."

_WARN_OUTPUT_SUPPRESSED = "All output data suppressed by agent filter, but there is data available for agent types: {}"
_WARN_OUTPUT_MISSING = "Provided file did not contain any output data, only input recovery available."
_INFO_MEMORY_SAVING = "Memory saving mode enabled: Disable on conversion of small files for performance improvements."


def _read_and_extract_data(config: dict[Options, Any]) -> None:
    """Read protobuf file, extracts, converts, and saves the converted data.

    Args:
        config: script configuration options

    Raises:
        OutputError: if file could not be opened or converted, logged with level "ERROR"
    """
    file_path = Path(config[Options.FILE])
    log().info("Opening file for reading...")
    try:
        with open(file_path, "rb") as file_stream:
            _extract_and_convert_data(config, file_stream, file_path)
    except OSError as ex:
        raise log_error(OutputError(_ERR_FILE_OPEN_FAIL.format(file_path))) from ex


def _extract_and_convert_data(config: dict[Options, Any], file_stream: BinaryIO, file_path: Path) -> None:
    """Extracts data from provided input file stream, converts it, and writes the result to output files.

    Args:
        config: script configuration options
        file_stream: opened input file
        file_path: path to input file

    Raises:
        OutputError: if file could not be opened or converted, logged with level "ERROR"
    """
    log().info("Reading and extracting data...")
    output_writer = CsvWriter(config[Options.OUTPUT], file_path, config[Options.SINGLE_AGENT_EXPORT])
    agent_type_log = AgentTypeLog(_agent_name_filter_list=config[Options.AGENT_LIST])
    data_transformer = DataTransformer.build(config[Options.RESOLVE_COMPLEX_FIELD])
    reader = Reader.get_reader(file=file_stream, read_single=config[Options.MEMORY_SAVING])
    input_dao = InputDao()
    execution_dao = ExecutionDao()
    while data_storages := reader.read():
        execution_dao.store_execution_metadata(data_storages)
        if config[Options.INPUT_RECOVERY]:
            input_dao.store_inputs(data_storages)
        output = OutputDAO(data_storages, agent_type_log)
        for agent_name in output.get_sorted_agents_to_extract():
            log().debug(f"Extracting data for {agent_name}...")
            data_frames = output.get_agent_data(agent_name, data_transformer)
            if not config[Options.MEMORY_SAVING]:
                apply_time_merging(data_frames, config[Options.TIME_MERGING])
                apply_time_option(data_frames, config[Options.TIME])
            log().debug(f"Writing data for {agent_name}...")
            output_writer.write_to_files(agent_name, data_frames)

    if config[Options.INPUT_RECOVERY]:
        _recover_inputs(config, input_dao, execution_dao.get_fameio_version())
    if config[Options.MEMORY_SAVING]:
        _memory_saving_apply_conversions(config, output_writer)

    if not agent_type_log.has_any_agent_type():
        if len(agent_type_log.get_agents_with_output()) > 0:
            log().warning(_WARN_OUTPUT_SUPPRESSED.format(agent_type_log.get_agents_with_output()))
        else:
            log().warning(_WARN_OUTPUT_MISSING)
    log().info("Data conversion completed.")


def _recover_inputs(config: dict[Options, Any], input_dao: InputDao, fameio_version: str) -> None:
    """Reads scenario configuration from provided `input_dao`.

    Args:
        config: script configuration options
        input_dao: to recover the input data from
        fameio_version: version of fameio that was used to create the input data

    Raises:
        OutputError: if inputs could not be recovered or saved to files, logged with level "ERROR"
    """
    log().info("Recovering inputs...")
    try:
        timeseries, scenario = input_dao.recover_inputs()
    except InputError as ex:
        raise log_error(OutputError(_ERR_RECOVER_INPUT.format(fameio_version))) from ex
    base_path = config[Options.OUTPUT] if config[Options.OUTPUT] is not None else "./"
    series_writer = CsvWriter(
        config_output=Path(base_path, "./recovered"), input_file_path=Path("./"), single_export=False
    )
    series_writer.write_all_time_series_to_disk(timeseries)
    data_to_yaml_file(scenario.to_dict(), Path(base_path, "./recovered/scenario.yaml"))


def _memory_saving_apply_conversions(config: dict[Options, Any], output_writer: CsvWriter) -> None:
    """Rewrite result files: applies time-merging and time conversion options on a per-file basis.

    This is only required in memory saving mode.

    Args:
        config: script configuration options
        output_writer: to rewrite the previously written files

    Raises:
        OutputError: in case files could not be read, converted, or re-written, logged with level "ERROR"
    """
    log().info("Applying time conversion and merging options to extracted files...")
    written_files = output_writer.pop_all_file_paths()
    for agent_name, file_path in written_files.items():
        parsed_data: dict[str | None, pd.DataFrame] = {None: pd.read_csv(file_path, sep=";", index_col=INDEX)}
        apply_time_merging(parsed_data, config[Options.TIME_MERGING])
        apply_time_option(parsed_data, config[Options.TIME])
        output_writer.write_to_files(agent_name, parsed_data)


def run(config: dict[Options, Any] | None = None) -> None:
    """Reads configured file in protobuf format and extracts its content to .CSV and .YAML file(s).

    Args:
        config: script configuration options

    Raises:
        ScriptError: if any kind of expected error or a memory error occurred, logged with level "CRITICAL"
    """
    config = update_default_config(config, DEFAULT_CONFIG)
    fameio_logger(log_level_name=config[Options.LOG_LEVEL], file_name=config[Options.LOG_FILE])
    if config[Options.MEMORY_SAVING]:
        log().info(_INFO_MEMORY_SAVING)

    try:
        try:
            _read_and_extract_data(config)
        except MemoryError as ex:
            error = OutputError(_ERR_MEMORY_SEVERE if config[Options.MEMORY_SAVING] else _ERR_OUT_OF_MEMORY)
            raise log_critical(error) from ex
    except OutputError as ex:
        raise log_critical(ScriptError(_ERR_FAIL)) from ex


if __name__ == "__main__":
    cli_config = handle_args(sys.argv[1:])
    try:
        run(cli_config)
    except ScriptError as e:
        raise SystemExit(1) from e
