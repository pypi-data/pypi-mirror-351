# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Final

from fameio.logs import log
from fameio.time import FameTime
from fameio.tools import keys_to_lower
from .exception import get_or_raise


class GeneralProperties:
    """Hosts general properties of a scenario."""

    KEY_RUN: Final[str] = "RunId".lower()
    KEY_SIMULATION = "Simulation".lower()
    KEY_START = "StartTime".lower()
    KEY_STOP = "StopTime".lower()
    KEY_SEED = "RandomSeed".lower()

    _ERR_MISSING_KEY = "General Properties requires key '{}' but it is missing."
    _ERR_SIMULATION_DURATION = "Simulation starts after its end time - check start and stop times."

    def __init__(
        self,
        run_id: int,
        simulation_start_time: int,
        simulation_stop_time: int,
        simulation_random_seed: int,
    ) -> None:
        if simulation_stop_time < simulation_start_time:
            log().warning(GeneralProperties._ERR_SIMULATION_DURATION)
        self._run_id = run_id
        self._simulation_start_time = simulation_start_time
        self._simulation_stop_time = simulation_stop_time
        self._simulation_random_seed = simulation_random_seed

    @classmethod
    def from_dict(cls, definitions: dict) -> GeneralProperties:
        """Parses general properties from provided `definitions`.

        Args:
            definitions: dictionary representation of general properties

        Returns:
            new GeneralProperties

        Raises:
            ScenarioError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        definitions = keys_to_lower(definitions)
        run_id = definitions.get(GeneralProperties.KEY_RUN, 1)

        simulation_definition = keys_to_lower(
            get_or_raise(
                definitions,
                GeneralProperties.KEY_SIMULATION,
                GeneralProperties._ERR_MISSING_KEY,
            )
        )
        start_time = FameTime.convert_string_if_is_datetime(
            get_or_raise(
                simulation_definition,
                GeneralProperties.KEY_START,
                GeneralProperties._ERR_MISSING_KEY,
            )
        )
        stop_time = FameTime.convert_string_if_is_datetime(
            get_or_raise(
                simulation_definition,
                GeneralProperties.KEY_STOP,
                GeneralProperties._ERR_MISSING_KEY,
            )
        )
        random_seed = simulation_definition.get(GeneralProperties.KEY_SEED, 1)
        return cls(run_id, start_time, stop_time, random_seed)

    def to_dict(self) -> dict:
        """Serializes the general properties to a dict."""
        result: dict = {self.KEY_RUN: self._run_id}
        simulation_dict = {
            self.KEY_START: self.simulation_start_time,
            self.KEY_STOP: self.simulation_stop_time,
            self.KEY_SEED: self.simulation_random_seed,
        }
        result[self.KEY_SIMULATION] = simulation_dict
        return result

    @property
    def run_id(self) -> int:
        """Returns the run ID."""
        return self._run_id

    @property
    def simulation_start_time(self) -> int:
        """Returns the simulation start time."""
        return self._simulation_start_time

    @property
    def simulation_stop_time(self) -> int:
        """Returns the simulation stop time."""
        return self._simulation_stop_time

    @property
    def simulation_random_seed(self) -> int:
        """Returns the simulation random seed."""
        return self._simulation_random_seed
