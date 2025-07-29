# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from os import path
from typing import IO, Final

import yaml

from fameio.input import YamlLoaderError
from fameio.logs import log, log_critical


class FameYamlLoader(yaml.SafeLoader):
    """Custom YAML Loader for `!include` constructor."""

    INCLUDE_COMMAND: Final[str] = "!include"

    _ERR_ARGUMENT_COUNT = "!include supports only one or two arguments in list but was: '{}'"
    _ERR_FILE_KEY_MISSING = "Could not find key 'file' on !include statement in mapping format: {}"
    _ERR_NODE_TYPE = "YAML node type not implemented: {}"
    _DEBUG_LOADER_INIT = "Initializing custom YAML loader"
    _DEBUG_SCALAR_NODE = "Found !include in scalar format. File(s) to include: {}"
    _DEBUG_SEQUENCE_NODE = "Found !include in sequence format. File(s) to include: {}; Restricted to nodes: {}"
    _DEBUG_MAPPING_NODE = "Found !include in mapping format. File(s) to include: {}; Restricted to nodes: {}"

    def __init__(self, stream: IO) -> None:
        log().debug(self._DEBUG_LOADER_INIT)
        self._root_path = path.split(stream.name)[0] if stream.name is not None else path.curdir
        super().__init__(stream)

    def digest_include(self, node: yaml.Node) -> tuple[str, str, str]:
        """Reads arguments in an !include statement and returns information which files to include.

        Args:
            node: the current node that is to be deconstructed; could be a file-pattern to load;
                  or a list of 1-2 arguments, with the first being the file pattern and
                  the other being a node address string; or a dict that maps "file" to the pattern
                  and "node" to the node address string

        Returns:
            Tuple of (`root`, `file_pattern`, `node_pattern`), where
              `root` is a path to the current file that was read by this FameYamlLoader,
              `files` is a file pattern,
              and nodes is an optional address (list of nodes) for name for the node that is to be returned

        Raises:
            YamlLoaderError: If !include statement could not be interpreted, logged with level "CRITICAL"
        """
        if isinstance(node, yaml.nodes.ScalarNode):
            file_pattern, node_string = self._read_scalar_node(node)
        elif isinstance(node, yaml.nodes.SequenceNode):
            file_pattern, node_string = self._read_sequence_node(node)
        elif isinstance(node, yaml.nodes.MappingNode):
            file_pattern, node_string = self._read_mapping_node(node)
        else:
            raise log_critical(YamlLoaderError(self._ERR_NODE_TYPE.format(node)))
        return self._root_path, file_pattern, node_string

    def _read_scalar_node(self, args: yaml.nodes.ScalarNode) -> tuple[str, str]:
        """Reads and returns content of a scalar !include statement.

        Example: !include "file".

        Args:
            args: argument assigned to the !include statement

        Returns:
           given argument converted to string, an empty string since no node-address can be specified in scalar syntax
        """
        file_pattern = self.construct_scalar(args)
        log().debug(self._DEBUG_SCALAR_NODE.format(file_pattern))
        return str(file_pattern), ""

    def _read_sequence_node(self, args: yaml.nodes.SequenceNode) -> tuple[str, str]:
        """Reads and returns content of a sequence !include statement.

        Example: !include ["file", Path:to:Node].

        Args:
            args: argument assigned to the !include statement

        Returns:
            first part of argument as file path, the second part of argument as node-address

        Raises:
            YamlLoaderError: if argument count is not 1 or 2, logged with level "CRITICAL"
        """
        argument_list = self.construct_sequence(args)
        if len(argument_list) not in [1, 2]:
            raise log_critical(YamlLoaderError(self._ERR_ARGUMENT_COUNT.format(str(args))))

        file_pattern = argument_list[0]
        node_string = argument_list[1] if len(argument_list) == 2 else ""
        log().debug(self._DEBUG_SEQUENCE_NODE.format(file_pattern, node_string))
        return file_pattern, node_string

    def _read_mapping_node(self, args: yaml.nodes.MappingNode) -> tuple[str, str]:
        """Reads and returns content of a mapping !include statement.

        Example: !include {file="file", node="Path:to:Node"}

        Args:
            args: argument assigned to the !include statement

        Returns:
            file argument as file path, node argument as node-address

        Raises:
            YamlLoaderError: if "file" key is missing, logged with level "CRITICAL"
        """
        argument_map = {str(k).lower(): v for k, v in self.construct_mapping(args).items()}
        if "file" not in argument_map.keys():
            raise log_critical(YamlLoaderError(self._ERR_FILE_KEY_MISSING.format(str(args))))

        file_pattern = argument_map["file"]
        node_string = argument_map.get("node", "")
        log().debug(self._DEBUG_MAPPING_NODE.format(file_pattern, node_string))
        return file_pattern, node_string
