# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any, Final

from fameprotobuf.data_storage_pb2 import DataStorage
from fameprotobuf.execution_data_pb2 import ExecutionData
from google.protobuf import message

from fameio.logs import log_error
from fameio.output import OutputError


class ExecutionDataError(OutputError):
    """Indicates an error during reconstruction of execution metadata from its protobuf representation."""


VERSION_MAP: Final[dict[str, str]] = {
    "fame_protobuf": "FameProtobuf",
    "fame_io": "FameIo",
    "fame_core": "FameCore",
    "python": "Python",
    "jvm": "JavaVirtualMachine",
    "os": "OperatingSystem",
}
PROCESS_MAP: Final[dict[str, str]] = {
    "core_count": "NumberOfCores",
    "output_interval": "OutputIntervalInTicks",
    "output_process": "ProcessControllingOutputs",
}
STATISTICS_MAP: Final[dict[str, str]] = {
    "start": "SimulationBeginInRealTime",
    "duration_in_ms": "SimulationWallTimeInMillis",
    "tick_count": "SimulatedTicks",
}


class ExecutionDao:
    """Data access object for execution metadata saved in protobuf."""

    _ERR_MULTIPLE_VERSIONS = "More than two version metadata sections found: File is corrupt."
    _ERR_MULTIPLE_CONFIGURATIONS = "More than one configuration metadata section found: File is corrupt."
    _ERR_MULTIPLE_SIMULATIONS = "More than one simulation metadata section found: File is corrupt."
    _ERR_NO_VERSION = "No version data found: File is either corrupt or was created with fameio version < 3.0."

    KEY_COMPILATION: Final[str] = "InputCompilation"
    KEY_RUN: Final[str] = "ModelRun"
    KEY_VERSIONS: Final[str] = "SoftwareVersions"
    KEY_PROCESSES: Final[str] = "ProcessConfiguration"
    KEY_STATISTICS: Final[str] = "Statistics"

    def __init__(self) -> None:
        self._compile_versions: ExecutionData.VersionData | None = None
        self._run_versions: ExecutionData.VersionData | None = None
        self._run_configuration: ExecutionData.ProcessConfiguration | None = None
        self._run_simulation: ExecutionData.Simulation | None = None

    def store_execution_metadata(self, data_storages: list[DataStorage]) -> None:
        """Scans given data storages for execution metadata.

        If metadata are present, they are extracted for later inspection

        Args:
            data_storages: to be scanned for execution metadata

        Raises:
            ExecutionDataError: if more execution sections are found than expected, logged with level "ERROR"
        """
        for entry in [storage.execution for storage in data_storages if storage.HasField("execution")]:
            if entry.HasField("version_data"):
                self._add_version_data(entry.version_data)
            if entry.HasField("configuration"):
                self._add_configuration(entry.configuration)
            if entry.HasField("simulation"):
                self._add_simulation(entry.simulation)

    def _add_version_data(self, data: ExecutionData.VersionData) -> None:
        """Stores given version metadata.

        Args:
            data: version data saved during compilation (first call), or during model run (second call)

        Raises:
            ExecutionDataError: if both version data are already set, logged with level "ERROR"
        """
        if not self._compile_versions:
            self._compile_versions = data
        elif not self._run_versions:
            self._run_versions = data
        else:
            raise log_error(ExecutionDataError(self._ERR_MULTIPLE_VERSIONS))

    def _add_configuration(self, data: ExecutionData.ProcessConfiguration) -> None:
        """Stores given process configuration metadata.

        Args:
            data: process configuration data to be saved

        Raises:
            ExecutionDataError: if process configuration data are already set, logged with level "ERROR"
        """
        if not self._run_configuration:
            self._run_configuration = data
        else:
            raise log_error(ExecutionDataError(self._ERR_MULTIPLE_CONFIGURATIONS))

    def _add_simulation(self, data: ExecutionData.Simulation) -> None:
        """Stores given simulation metadata.

        Args:
            data: simulation metadata to be stored

        Raises:
            ExecutionDataError: if simulation metadata are already set, logged with level "ERROR"
        """
        if not self._run_simulation:
            self._run_simulation = data
        else:
            raise log_error(ExecutionDataError(self._ERR_MULTIPLE_SIMULATIONS))

    def get_fameio_version(self) -> str:
        """Gets version of fameio used to create the input data.

        Returns:
            fameio version that was used to create the input data

        Raises:
            ExecutionDataError: if fameio version could not be read, logged with level "ERROR"
        """
        if self._compile_versions:
            return self._compile_versions.fame_io
        raise log_error(ExecutionDataError(self._ERR_NO_VERSION))

    def get_metadata_dict(self) -> dict[str, Any]:
        """Creates a dictionary from all provided execution metadata.

        Returns:
            dictionary with all execution metadata currently stored in this DAO
        """
        result = {
            self.KEY_COMPILATION: {self.KEY_VERSIONS: self._get_dict(self._compile_versions, VERSION_MAP)},
            self.KEY_RUN: {
                self.KEY_VERSIONS: self._get_dict(self._run_versions, VERSION_MAP),
                self.KEY_PROCESSES: self._get_dict(self._run_configuration, PROCESS_MAP),
                self.KEY_STATISTICS: self._get_dict(self._run_simulation, STATISTICS_MAP),
            },
        }
        return result

    @staticmethod
    def _get_dict(data: message, replacements: dict[str, str]) -> dict[str, str]:
        """Searches for `replacements.keys()` in provided `data`.

        If key is available, saves the corresponding data item to dict, associated to a name matching the value in `replacements`.

        Args:
            data: to extract data from
            replacements: keys to be replaced by their values in the resulting dict

        Returns:
            a dictionary matching entries from `data` with their new keys as specified under "replacements"
        """
        versions = {}
        if data is not None:
            for key, replacement in replacements.items():
                if data.HasField(key):
                    versions[replacement] = getattr(data, key)
        return versions
