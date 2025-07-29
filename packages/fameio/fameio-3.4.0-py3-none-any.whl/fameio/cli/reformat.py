# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
from typing import Any

from fameio.cli.options import Options
from fameio.cli.parser import (
    map_namespace_to_options_dict,
    add_logfile_argument,
    add_log_level_argument,
    add_file_pattern_argument,
    add_replace_argument,
)

CLI_DEFAULTS = {
    Options.LOG_LEVEL: "WARN",
    Options.LOG_FILE: None,
    Options.FILE_PATTERN: None,
    Options.REPLACE: False,
}


def handle_args(args: list[str], defaults: dict[Options, Any] | None = None) -> dict[Options, Any]:
    """Converts given `args` and returns a configuration for the transform script.

    Args:
        args: list of (command line) arguments, e.g., ['-fp', 'my_file']; arg values take precedence over defaults
        defaults: optional default values used for unspecified parameters; missing defaults are replaced by CLI defaults

    Returns:
        final configuration compiled from (given) `defaults` and given `args`
    """
    parser = _prepare_parser(defaults)
    parsed = parser.parse_args(args)
    return map_namespace_to_options_dict(parsed)


def _prepare_parser(defaults: dict[Options, Any] | None) -> argparse.ArgumentParser:
    """Creates a parser with given defaults to handle `reformat` configuration arguments.

    Returns:
        new parser using given defaults for its arguments; if a default is not specified, hard-coded defaults are used
    """
    defaults = defaults if (defaults is not None) else {}
    parser = argparse.ArgumentParser()
    add_log_level_argument(parser, _get_default(defaults, Options.LOG_LEVEL))
    add_logfile_argument(parser, _get_default(defaults, Options.LOG_FILE))
    add_file_pattern_argument(parser, _get_default(defaults, Options.FILE_PATTERN))
    add_replace_argument(parser, _get_default(defaults, Options.REPLACE))
    return parser


def _get_default(defaults: dict, option: Options) -> Any:
    """Returns default for given `option` or its cli default."""
    return defaults.get(option, CLI_DEFAULTS[option])
