# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
from typing import Any

from fameio.cli.options import Options, ResolveOptions, TimeOptions
from fameio.cli.parser import (
    add_file_argument,
    add_log_level_argument,
    add_logfile_argument,
    add_output_argument,
    add_select_agents_argument,
    add_single_export_argument,
    add_memory_saving_argument,
    add_resolve_complex_argument,
    add_time_argument,
    add_merge_time_argument,
    add_inputs_recovery_argument,
    map_namespace_to_options_dict,
)

CLI_DEFAULTS = {
    Options.FILE: None,
    Options.LOG_LEVEL: "WARN",
    Options.LOG_FILE: None,
    Options.OUTPUT: None,
    Options.AGENT_LIST: None,
    Options.SINGLE_AGENT_EXPORT: False,
    Options.MEMORY_SAVING: False,
    Options.RESOLVE_COMPLEX_FIELD: ResolveOptions.SPLIT,
    Options.TIME: TimeOptions.UTC,
    Options.TIME_MERGING: None,
    Options.INPUT_RECOVERY: False,
}

_INFILE_PATH_HELP = "Provide path to protobuf file"
_OUTFILE_PATH_HELP = "Provide path to folder to store output .csv files"


def handle_args(args: list[str], defaults: dict[Options, Any] | None = None) -> dict[Options, Any]:
    """Handles command line arguments and returns `run_config` for convert_results script.

    Args:
        args: list of (command line) arguments, e.g., ['-f', 'my_file']; arg values take precedence over defaults
        defaults: optional default values used for unspecified parameters; missing defaults are replaced by CLI defaults

    Returns:
        final configuration compiled from (given) `defaults` and given `args`
    """
    parser = _prepare_parser(defaults)
    parsed = parser.parse_args(args)
    return map_namespace_to_options_dict(parsed)


def _prepare_parser(defaults: dict[Options, Any] | None) -> argparse.ArgumentParser:
    """Creates a parser with given defaults to handle `make_config` configuration arguments.

    Returns:
        new parser using given defaults for its arguments; if a default is not specified, hard-coded defaults are used
    """
    defaults = defaults if (defaults is not None) else {}
    parser = argparse.ArgumentParser()

    add_file_argument(parser, _get_default(defaults, Options.FILE), _INFILE_PATH_HELP)
    add_log_level_argument(parser, _get_default(defaults, Options.LOG_LEVEL))
    add_logfile_argument(parser, _get_default(defaults, Options.LOG_FILE))
    add_output_argument(parser, _get_default(defaults, Options.OUTPUT), _OUTFILE_PATH_HELP)
    add_select_agents_argument(parser, _get_default(defaults, Options.AGENT_LIST))
    add_single_export_argument(parser, _get_default(defaults, Options.SINGLE_AGENT_EXPORT))
    add_memory_saving_argument(parser, _get_default(defaults, Options.MEMORY_SAVING))
    add_resolve_complex_argument(parser, _get_default(defaults, Options.RESOLVE_COMPLEX_FIELD))
    add_time_argument(parser, _get_default(defaults, Options.TIME))
    add_merge_time_argument(parser, _get_default(defaults, Options.TIME_MERGING))
    add_inputs_recovery_argument(parser, _get_default(defaults, Options.INPUT_RECOVERY))

    return parser


def _get_default(defaults: dict, option: Options) -> Any:
    """Returns default for given `option` or its cli default."""
    return defaults.get(option, CLI_DEFAULTS[option])
