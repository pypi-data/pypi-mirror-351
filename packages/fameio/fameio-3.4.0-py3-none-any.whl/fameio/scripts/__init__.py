#!/usr/bin/env python
import sys

from fameio.scripts.convert_results import DEFAULT_CONFIG as DEFAULT_CONVERT_CONFIG
from fameio.scripts.convert_results import run as convert_results
from fameio.scripts.exception import ScriptError
from fameio.scripts.make_config import run as make_config
from fameio.scripts.reformat import run as reformat
from fameio.cli.convert_results import handle_args as handle_convert_results_args
from fameio.cli.make_config import handle_args as handle_make_config_args
from fameio.cli.reformat import handle_args as handle_reformat_args


# noinspection PyPep8Naming
def makeFameRunConfig():
    cli_config = handle_make_config_args(sys.argv[1:])
    try:
        make_config(cli_config)
    except ScriptError as e:
        raise SystemExit(1) from e


# noinspection PyPep8Naming
def convertFameResults():
    cli_config = handle_convert_results_args(sys.argv[1:], DEFAULT_CONVERT_CONFIG)
    try:
        convert_results(cli_config)
    except ScriptError as e:
        raise SystemExit(1) from e


# noinspection PyPep8Naming
def reformatTimeSeries():
    cli_config = handle_reformat_args(sys.argv[1:])
    try:
        reformat(cli_config)
    except ScriptError as e:
        raise SystemExit(1) from e
