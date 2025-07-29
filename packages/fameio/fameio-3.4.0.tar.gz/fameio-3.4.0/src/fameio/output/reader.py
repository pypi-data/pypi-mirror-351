# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from typing import IO, final, NoReturn

from fameprotobuf.data_storage_pb2 import DataStorage
from google.protobuf.message import DecodeError

import fameio
from fameio.logs import log, log_critical, log_error
from fameio.output import OutputError


class ProtobufReaderError(OutputError):
    """Indicates an error while reading a protobuf file."""


class Reader(ABC):
    """Abstract base class for protobuf file readers."""

    _ERR_FILE_READ = "Could not read file content."
    _ERR_HEADER_UNRECOGNISED = ""
    _ERR_FILE_CORRUPT_NEGATIVE_LENGTH = "Corrupt file, message length must be positive."
    _ERR_FILE_CORRUPT_MISSING_DATA = "Trying to read corrupt file caused by inconsistent message length."
    _ERR_UNSUPPORTED_MODE = "Ignoring memory saving mode: not supported for files created with `fame-core<1.4`."
    _ERR_PARSING_FAILED = "File Corrupt. Could not parse file content."
    _WARN_NO_HEADER = "No header recognised in file. File might be deprecated or corrupted."
    _DEBUG_FILE_END_REACHED = "Reached expected end of file."

    _HEADER_LENGTH = 30
    HEADER_ENCODING = "utf-8"
    BYTES_DEFINING_MESSAGE_LENGTH = 4

    _ERR_DEPRECATED_V0 = "Cannot read file: File was created with `FAME-Core` version <1.4 or `fameio` version < 1.6"
    _ERR_DEPRECATED_V1 = "Cannot read file: File was created with `FAME-Core` version <2.0 or `fameio` version < 3.0"

    _READER_HEADERS = {
        None: lambda file, mode: Reader._raise_error(Reader._ERR_DEPRECATED_V0),
        fameio.FILE_HEADER_V1: lambda file, mode: Reader._raise_error(Reader._ERR_DEPRECATED_V1),
        fameio.FILE_HEADER_V2: lambda file, mode: ReaderV2(file, mode),  # pylint: disable=unnecessary-lambda
    }

    @staticmethod
    @final
    def _raise_error(error_message: str) -> NoReturn:
        raise log_critical(ProtobufReaderError(error_message))

    def __init__(self, file: IO, read_single) -> None:
        self._file = file
        self._read_single = read_single

    @abstractmethod
    def read(self) -> list[DataStorage]:
        """Reads associated filestream and returns one or multiple DataStorage(s) or empty list.

        Returns:
            one or multiple DataStorage protobuf object(s) read from file

        Raises:
            ProtobufReaderError: if file is corrupted in any way, logged with level "ERROR"
        """

    @staticmethod
    def get_reader(file: IO, read_single: bool = False) -> Reader:
        """Returns reader matching the given file header.

        Args:
            file: to be read by the returned Reader
            read_single: if True, the returned Reader's `read()` method gets one messages at a time

        Returns:
            Reader that can read the specified file

        Raises:
            ProtobufReaderError: if file has an unsupported header,logged with level "CRITICAL"
        """
        log().debug("Reading file headers...")
        try:
            header_content = file.read(Reader._HEADER_LENGTH)
        except ValueError as e:
            raise log_critical(ProtobufReaderError(Reader._ERR_FILE_READ)) from e

        try:
            header = header_content.decode(Reader.HEADER_ENCODING)
        except UnicodeDecodeError:
            header = None
            log().warning(Reader._WARN_NO_HEADER)

        if header not in Reader._READER_HEADERS:
            header = None

        return Reader._READER_HEADERS[header](file, read_single)

    @final
    def _read_message_length(self) -> int:
        """Returns length of next DataStorage message in file."""
        message_length_byte = self._file.read(self.BYTES_DEFINING_MESSAGE_LENGTH)
        if not message_length_byte:
            log().debug(self._DEBUG_FILE_END_REACHED)
            message_length_int = 0
        else:
            message_length_int = struct.unpack(">i", message_length_byte)[0]
        return message_length_int

    @final
    def _read_data_storage_message(self, message_length: int | None = None) -> DataStorage:
        """Returns data storage read from current file position and following `message_length` bytes.

        If `message_length` is omitted, the rest of the file is read. If no message is found, None is returned.

        Args:
            message_length: amounts of bytes to read - must correspond to the next DataStorage message in file

        Returns:
            Read and de-serialised DataStorage

        Raises:
            ProtobufReaderError: if message_length is corrupt or file is corrupt, logged with level "ERROR"
        """
        if message_length is None:
            message = self._file.read()
        elif message_length > 0:
            message = self._file.read(message_length)
        else:
            raise log_error(ProtobufReaderError(self._ERR_FILE_CORRUPT_NEGATIVE_LENGTH))
        if message_length and len(message) != message_length:
            raise log_error(ProtobufReaderError(self._ERR_FILE_CORRUPT_MISSING_DATA))
        return self._parse_to_data_storage(message) if message else None

    @staticmethod
    @final
    def _parse_to_data_storage(message: bytes) -> DataStorage:
        """
        De-serialises a binary message into a DataStorage protobuf object

        Args:
            message: to be convert

        Returns:
            DataStorage initialised from the given message

        Raises:
            ProtobufReaderError: if message could not be converted, logged with level "ERROR"
        """
        data_storage = DataStorage()
        try:
            data_storage.ParseFromString(message)
        except DecodeError as e:
            raise log_error(ProtobufReaderError(Reader._ERR_PARSING_FAILED)) from e
        return data_storage


class ReaderV2(Reader):
    """Reader class for `fame-core>=2.0` output with header of version v002."""

    def read(self) -> list[DataStorage]:
        messages = []
        while True:
            message_length = self._read_message_length()
            if message_length == 0:
                break
            messages.append(self._read_data_storage_message(message_length))
            if self._read_single:
                break
        log().debug(f"Read {len(messages)} messages from file.")
        return messages
