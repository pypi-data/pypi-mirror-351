# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import argparse
from enum import Enum, auto


class ParsableEnum(Enum):
    """Extend this to create an enum that can be parsed with argparse."""

    @classmethod
    def instantiate(cls, name: str) -> Enum:
        try:
            return cls[name]
        except KeyError as e:
            raise argparse.ArgumentTypeError(f"'{name}' is not a valid option") from e

    def __str__(self):
        return self.name


class Options(Enum):
    """Specifies command line configuration options."""

    FILE = auto()
    LOG_LEVEL = auto()
    LOG_FILE = auto()
    OUTPUT = auto()
    AGENT_LIST = auto()
    SINGLE_AGENT_EXPORT = auto()
    MEMORY_SAVING = auto()
    RESOLVE_COMPLEX_FIELD = auto()
    TIME = auto()
    TIME_MERGING = auto()
    INPUT_RECOVERY = auto()
    INPUT_ENCODING = auto()
    FILE_PATTERN = auto()
    REPLACE = auto()


class TimeOptions(ParsableEnum, Enum):
    """Specifies options for conversion of time in output."""

    INT = auto()
    UTC = auto()
    FAME = auto()


class ResolveOptions(ParsableEnum, Enum):
    """Specifies options for resolving complex fields in output files."""

    IGNORE = auto()
    SPLIT = auto()
