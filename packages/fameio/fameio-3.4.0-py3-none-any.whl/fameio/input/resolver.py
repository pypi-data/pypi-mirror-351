# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import glob
from os import path


class PathResolver:
    """Class responsible for locating files referenced in a scenario.

    Such files can be the ones referenced via the YAML `!include` extension, or simply the data files (time_series)
    referenced in attributes.

    This class provides a default behaviour that can easily be customized by the caller.
    """

    # noinspection PyMethodMayBeStatic
    def resolve_file_pattern(self, root_path: str, file_pattern: str) -> list[str]:
        """Returns a list of file paths matching the given `file_pattern` in the specified `root_path`."""
        absolute_path = path.abspath(path.join(root_path, file_pattern))
        return glob.glob(absolute_path)

    # noinspection PyMethodMayBeStatic
    def resolve_series_file_path(self, file_name: str) -> str | None:
        """Searches for the file in the current working directory and returns its absolute file path.

        Args:
            file_name: name of the file that is to be searched

        Returns:
            absolute path to given file_name if file_name is an absolute path on its own;
            or relative path to given file_name if the file was found on the current directory;
            or None if file could not be found
        """
        return file_name if path.isabs(file_name) else PathResolver._search_file_in_directory(file_name, path.curdir)

    @staticmethod
    def _search_file_in_directory(file_name: str, directory: str) -> str | None:
        """Returns path to `file_name` relative to specified `directory` if file was found there, None otherwise."""
        file_path = path.join(directory, file_name)
        return file_path if path.exists(file_path) else None
