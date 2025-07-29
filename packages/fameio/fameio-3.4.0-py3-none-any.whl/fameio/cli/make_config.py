# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from fameio.cli.options import Options
from fameio.cli.parser import (
    add_file_argument,
    add_log_level_argument,
    add_logfile_argument,
    add_output_argument,
    map_namespace_to_options_dict,
    add_encoding_argument,
)

CLI_DEFAULTS = {
    Options.FILE: None,
    Options.LOG_LEVEL: "WARN",
    Options.LOG_FILE: None,
    Options.OUTPUT: Path("config.pb"),
    Options.INPUT_ENCODING: None,
}

_INFILE_PATH_HELP = "provide path to configuration file"
_OUTFILE_PATH_HELP = "provide file-path for the file to generate"
_ENCODING_HELP = (
    "provide encoding; will be applied to all input yaml files, "
    "for available encodings see https://docs.python.org/3.9/library/codecs.html#standard-encodings"
)


def handle_args(args: list[str], defaults: dict[Options, Any] | None = None) -> dict[Options, Any]:
    """Converts given `args` and returns a configuration for the make_config script.

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
    add_encoding_argument(parser, _get_default(defaults, Options.INPUT_ENCODING), _ENCODING_HELP)
    return parser


def _get_default(defaults: dict, option: Options) -> Any:
    """Returns default for given `option` or, if missing, its cli default."""
    return defaults.get(option, CLI_DEFAULTS[option])
