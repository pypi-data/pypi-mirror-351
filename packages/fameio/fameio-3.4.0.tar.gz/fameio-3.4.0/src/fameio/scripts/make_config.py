#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fameio.cli import update_default_config
from fameio.cli.make_config import handle_args, CLI_DEFAULTS as DEFAULT_CONFIG
from fameio.cli.options import Options
from fameio.input import InputError
from fameio.input.loader import load_yaml, validate_yaml_file_suffix
from fameio.input.scenario import Scenario
from fameio.input.validator import SchemaValidator
from fameio.input.writer import ProtoWriter
from fameio.logs import fameio_logger, log, log_critical
from fameio.scripts.exception import ScriptError

_ERR_FAIL: str = "Creation of run configuration file failed."


def run(config: dict[Options, Any] | None = None) -> None:
    """Executes the main workflow of building a FAME configuration file.

    Args:
        config: configuration options

    Raises:
        ScriptError: if any kind of expected error occurred, logged with level "CRITICAL"
    """
    config = update_default_config(config, DEFAULT_CONFIG)
    fameio_logger(log_level_name=config[Options.LOG_LEVEL], file_name=config[Options.LOG_FILE])

    try:
        file = config[Options.FILE]
        validate_yaml_file_suffix(Path(file))
        scenario_definition = load_yaml(Path(file), encoding=config[Options.INPUT_ENCODING])
        scenario = Scenario.from_dict(scenario_definition)
        SchemaValidator.check_agents_have_contracts(scenario)

        timeseries_manager = SchemaValidator.validate_scenario_and_timeseries(scenario)
        writer = ProtoWriter(config[Options.OUTPUT], timeseries_manager)
        writer.write_validated_scenario(scenario)
    except InputError as ex:
        raise log_critical(ScriptError(_ERR_FAIL)) from ex

    log().info("Configuration completed.")


if __name__ == "__main__":
    cli_config = handle_args(sys.argv[1:])
    try:
        run(cli_config)
    except ScriptError as e:
        raise SystemExit(1) from e
