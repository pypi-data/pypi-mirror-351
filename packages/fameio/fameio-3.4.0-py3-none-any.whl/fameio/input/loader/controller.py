# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
from typing import Callable, IO, Any, Final

import yaml

from fameio.input import YamlLoaderError
from fameio.input.loader.loader import FameYamlLoader
from fameio.input.resolver import PathResolver
from fameio.logs import log, log_critical


class LoaderController:
    """Controls loading of YAML files by spawning one FameYamlLoader per file.

    Uses same PathResolver and encoding for all files.
    """

    DISABLING_YAML_FILE_PREFIX: Final[str] = "IGNORE_"
    NODE_SPLIT_STRING: Final[str] = ":"

    _ERR_FILE_OPEN_ERROR = "Could not open file: '{}'"
    _ERR_FILE_LOAD_ERROR = "Could not parse YAML file due to errors in (line:column): ({}:{})"
    _ERR_NODE_MISSING = "'!include_node [{}, {}]': Cannot find '{}'"
    _ERR_NOT_LIST = "!include can only combine list-like elements from multiple files!"
    _WARN_NOTHING_TO_INCLUDE = "Could not find any files matching this '!include' directive '{}'"
    _INFO_FILE_IGNORED = "Ignoring file '{}' due to prefix '{}'"
    _DEBUG_SEARCH_NODE = "Searched file '{}' for node '{}'"
    _DEBUG_JOIN_COMPLETE = "Joined all files '{}' to joined data '{}'"
    _DEBUG_LOAD_FILE = "Loaded included YAML file '{}'"
    _DEBUG_FILES_INCLUDED = "!include directive '{}' yielded these files: '{}'"

    def __init__(self, path_resolver: PathResolver = PathResolver(), encoding: str | None = None) -> None:
        self._path_resolver = path_resolver
        self._encoding: str | None = encoding

    def load(self, yaml_file_path: Path) -> dict:
        """Spawns a new FameYamlLoader, loads the given `yaml_file_path` and returns its content.

        Args:
            yaml_file_path: path to YAML file that is to be loaded

        Returns:
            dictionary representation of loaded file

        Raises:
            YamlLoaderError: if file could not be read, logged with level "CRITICAL"
        """
        try:
            with open(yaml_file_path, "r", encoding=self._encoding) as configfile:
                try:
                    data = yaml.load(configfile, self._spawn_loader_builder())  # type: ignore[arg-type]
                except yaml.YAMLError as e:
                    line, column = self._get_problem_position(e)
                    raise log_critical(YamlLoaderError(self._ERR_FILE_LOAD_ERROR.format(line, column))) from e
        except OSError as e:
            raise log_critical(YamlLoaderError(self._ERR_FILE_OPEN_ERROR.format(yaml_file_path))) from e
        return data

    @staticmethod
    def _spawn_loader_builder() -> Callable[[IO], FameYamlLoader]:
        """Returns a new Callable that instantiates a new FameYamlLoader with an IO-stream."""
        return lambda stream: FameYamlLoader(stream)  # pylint: disable=unnecessary-lambda

    @staticmethod
    def _get_problem_position(exception: yaml.YAMLError) -> tuple[str, str]:
        """Returns problematic line and column from given error (if available).

        Args:
            exception: error thrown by yaml.load()

        Returns:
            Line and Column of error (if available), else a tuple of questions marks
        """
        if hasattr(exception, "problem_mark"):
            mark = exception.problem_mark
            return str(mark.line + 1), str(mark.column + 1)
        return "?", "?"

    def include(self, loader: FameYamlLoader, include_args: yaml.Node) -> Any:
        """Returns content loaded from the specified `include_args`.

        Args:
            loader: the YAML loader to be used to load the file(s) that are to be included
            include_args: arguments of include statement

        Returns:
            content of file as specified by include

        Raises:
            YamlLoaderError: If !include statement could not be interpreted, included files could not be read,
                or multiple included files could not be joined - logged with level "CRITICAL"
        """
        root_path, file_pattern, node_pattern = loader.digest_include(include_args)
        files = self._resolve_imported_path(root_path, file_pattern)
        nodes = node_pattern.split(self.NODE_SPLIT_STRING)

        joined_data = None
        for file_name in files:
            file_data = self.load(Path(file_name))
            extracted_node_data = self._extract_node(file_name, file_data, nodes)
            joined_data = self._join_data(extracted_node_data, joined_data)
            log().debug(self._DEBUG_LOAD_FILE.format(file_name))
        log().debug(self._DEBUG_JOIN_COMPLETE.format(files, joined_data))
        return joined_data

    def _resolve_imported_path(self, root_path: str, include_pattern: str) -> list[str]:
        """Returns a list of file paths matching the given `include_pattern` relative to the `root_path`.

        Ignores files starting with the `DISABLING_YAML_FILE_PREFIX`
        """
        file_list = self._path_resolver.resolve_file_pattern(root_path, include_pattern)
        ignore_filter = f"*{self.DISABLING_YAML_FILE_PREFIX}*"

        cleaned_file_list = []
        for file in file_list:
            if fnmatch(file, ignore_filter):
                log().info(self._INFO_FILE_IGNORED.format(file, self.DISABLING_YAML_FILE_PREFIX))
            else:
                cleaned_file_list.append(file)
        if not cleaned_file_list:
            log().warning(self._WARN_NOTHING_TO_INCLUDE.format(include_pattern))
        log().debug(self._DEBUG_FILES_INCLUDED.format(include_pattern, cleaned_file_list))
        return cleaned_file_list

    @staticmethod
    def _extract_node(file_name: str, data: dict, node_address: list[str]) -> Any:
        """Returns only the part of the data that is at the specified node address.

        Args:
            file_name: name of the file from which the data were read - used to enrich logging messages
            data: in which the given node address is searched for; only content below this address is returned
            node_address: list of nodes to be accessed in data; each node must be an inner element of the previous node

        Returns:
            Subset of the given data located at the specified node address

        Raises:
            YamlLoaderError: if any node in the address is not found
        """
        for node in node_address:
            if node:
                if node not in data.keys():
                    message = LoaderController._ERR_NODE_MISSING.format(file_name, node_address, node)
                    raise log_critical(YamlLoaderError(message))
                data = data[node]
        log().debug(LoaderController._DEBUG_SEARCH_NODE.format(file_name, node_address))
        return data

    @staticmethod
    def _join_data(new_data: list, previous_data: list | None) -> list:
        """Joins two lists with data to a larger list.

        Args:
            new_data: list of any data
            previous_data: list of any data

        Returns:
            previous data list extended by content of new data, or new data only if no previous data existed

        Raises:
            YamlLoaderError: if not both elements are lists
        """
        if not previous_data:
            return new_data
        if isinstance(new_data, list) and isinstance(previous_data, list):
            previous_data.extend(new_data)
            return previous_data
        raise log_critical(YamlLoaderError(LoaderController._ERR_NOT_LIST))
