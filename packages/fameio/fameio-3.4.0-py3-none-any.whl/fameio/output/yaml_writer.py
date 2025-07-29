# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import yaml

from fameio.logs import log, log_error
from fameio.output import OutputError

_ERR_OPEN_FILE = "Could not open file for reading: '{}'"

_INFO_DESTINATION = "Saving scenario to file at {}"


class YamlWriterError(OutputError):
    """An error occurred during writing a YAML file."""


def data_to_yaml_file(data: dict, file_path: Path) -> None:
    """Save the given data to a YAML file at given path.

    Args:
        data: to be saved to yaml file
        file_path: at which the file will be created

    Raises:
        YamlWriterError: if file could not be opened or written, logged with level "ERROR"
    """
    log().info(_INFO_DESTINATION.format(file_path))
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, encoding="utf-8")
    except OSError as e:
        raise log_error(YamlWriterError(_ERR_OPEN_FILE.format(file_path))) from e
