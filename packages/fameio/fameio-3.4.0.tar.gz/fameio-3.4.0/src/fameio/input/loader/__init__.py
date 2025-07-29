# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fameio.input import YamlLoaderError
from fameio.input.loader.controller import LoaderController
from fameio.input.loader.loader import FameYamlLoader
from fameio.input.resolver import PathResolver
from fameio.logs import log, log_critical

ALLOWED_SUFFIXES: tuple[str, ...] = (".yaml", ".yml")

_INFO_LOADING = "Loading YAML file at '{}'."
_ERR_NO_YAML_SUFFIX = "Only these file suffixes are allowed: {}, but the file suffix was: '{}'."

__CONTROLLERS: list[LoaderController] = [LoaderController()]


def _include_callback(own_loader: FameYamlLoader, args: yaml.Node) -> Any:
    """Uses single instance of _LoaderController to load data whenever an !include-command is found"""
    return __CONTROLLERS[0].include(own_loader, args)


# All FameYamlLoader use the same LoaderController - which can in turn spawn more FameYamlLoader
FameYamlLoader.add_constructor(FameYamlLoader.INCLUDE_COMMAND, _include_callback)


def load_yaml(yaml_file_path: Path, path_resolver: PathResolver = PathResolver(), encoding: str | None = None) -> dict:
    """Loads the YAML file from given `yaml_file_path` and returns its content as a dict.

    Args:
        yaml_file_path: Path to the YAML file that is to be read
        path_resolver: PathResolver to be used to resolve Paths specified within the YAML file
        encoding: of the YAML file (and all referenced YAML files using !include), platform default is used if omitted

    Returns:
        Content of the specified YAML file

    Raises:
        YamlLoaderError: if the YAML file could not be found, read, or parsed
    """
    log().info(_INFO_LOADING.format(yaml_file_path))
    _update_current_controller(path_resolver, encoding)
    return __CONTROLLERS[0].load(yaml_file_path)


def _update_current_controller(path_resolver: PathResolver, encoding: str | None) -> None:
    """Updates the current LoaderController to use the given `path_resolver` and `encoding`."""
    __CONTROLLERS[0] = LoaderController(path_resolver, encoding)


def validate_yaml_file_suffix(yaml_file: Path) -> None:
    """Ensures that given file has a file suffix compatible with YAML.

    Args:
        yaml_file: that is to be checked for suffix correctness

    Raises:
          YamlLoaderError: if given file has no YAML-associated file suffix, logged with level "CRITICAL"
    """
    if yaml_file.suffix.lower() not in ALLOWED_SUFFIXES:
        raise log_critical(YamlLoaderError(_ERR_NO_YAML_SUFFIX.format(ALLOWED_SUFFIXES, yaml_file)))
