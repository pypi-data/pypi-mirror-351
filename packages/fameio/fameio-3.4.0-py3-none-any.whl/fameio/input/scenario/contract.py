# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any, Final, overload

from fameio.input import InputError
from fameio.input.metadata import Metadata
from fameio.input.scenario.attribute import Attribute
from fameio.logs import log, log_error
from fameio.time import FameTime, ConversionError
from fameio.tools import keys_to_lower


class Contract(Metadata):
    """Contract between two Agents of a scenario."""

    class ContractError(InputError):
        """An error that occurred while parsing Contract definitions."""

    KEY_SENDER: Final[str] = "SenderId".lower()
    KEY_RECEIVER: Final[str] = "ReceiverId".lower()
    KEY_PRODUCT: Final[str] = "ProductName".lower()
    KEY_FIRST_DELIVERY: Final[str] = "FirstDeliveryTime".lower()
    KEY_INTERVAL: Final[str] = "DeliveryIntervalInSteps".lower()
    KEY_EVERY: Final[str] = "Every".lower()
    KEY_EXPIRE: Final[str] = "ExpirationTime".lower()
    KEY_ATTRIBUTES: Final[str] = "Attributes".lower()

    _ERR_MISSING_KEY = "Contract requires key '{}' but is missing it."
    _ERR_MULTI_CONTRACT_CORRUPT = (
        "Definition of Contracts is valid only for One-to-One, One-to-Many, Many-to-One, "
        "or N-to-N sender-to-receiver numbers. Found M-to-N pairing in Contract with "
        "Senders: {} and Receivers: {}."
    )
    _ERR_XOR_KEYS = "Contract expects exactly one of the keys '{}' or '{}'. Found either both or none."
    _ERR_INTERVAL_INVALID = "Contract delivery interval must be a positive integer but was: {}"
    _ERR_SENDER_IS_RECEIVER = "Contract sender and receiver have the same id: {}"
    _ERR_DOUBLE_ATTRIBUTE = "Cannot add attribute '{}' to contract because it already exists."
    _ERR_TIME_CONVERSION = "Contract item '{}' is an ill-formatted time: '{}'"
    _ERR_PRODUCT_EMPTY = f"A Contract's `{KEY_PRODUCT}` must be a non-emtpy string."

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        sender_id: int,
        receiver_id: int,
        product_name: str,
        delivery_interval: int,
        first_delivery_time: int,
        expiration_time: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Constructs a new Contract.

        Args:
            sender_id: unique id of sender
            receiver_id: unique id of receiver
            product_name: name of contracted product
            delivery_interval: time interval in steps between contract deliveries
            first_delivery_time: absolute time of first contract execution
            expiration_time: absolute time at which contract execution stops
            metadata: any metadata associated with the contract

        Returns:
            new Contract

        Raises:
            ContractError: if delivery interval is invalid, logged on level "ERROR"
        """
        super().__init__({self.KEY_METADATA: metadata} if metadata else None)
        if product_name.strip() == "":
            raise log_error(self.ContractError(self._ERR_PRODUCT_EMPTY))
        if sender_id == receiver_id:
            log().warning(self._ERR_SENDER_IS_RECEIVER.format(sender_id))
        if delivery_interval <= 0:
            raise log_error(self.ContractError(self._ERR_INTERVAL_INVALID.format(delivery_interval)))
        self._sender_id = sender_id
        self._receiver_id = receiver_id
        self._product_name = product_name
        self._delivery_interval = delivery_interval
        self._first_delivery_time = first_delivery_time
        self._expiration_time = expiration_time
        self._attributes: dict = {}

    def _notify_data_changed(self):
        """Placeholder method used to signal data changes to derived types."""

    @property
    def product_name(self) -> str:
        """Returns the product name of the contract."""
        return self._product_name

    @property
    def sender_id(self) -> int:
        """Returns the sender ID of the contract."""
        return self._sender_id

    @property
    def display_sender_id(self) -> str:
        """Returns the sender ID of the contract as a string for display purposes."""
        return f"#{self._sender_id}"

    @property
    def receiver_id(self) -> int:
        """Returns the receiver ID of the contract."""
        return self._receiver_id

    @property
    def display_receiver_id(self) -> str:
        """Returns the receiver ID of the contract as a string for display purposes."""
        return f"#{self._receiver_id}"

    @property
    def delivery_interval(self) -> int:
        """Returns the delivery interval of the contract (in steps)."""
        return self._delivery_interval

    @property
    def first_delivery_time(self) -> int:
        """Returns the first delivery time of the contract."""
        return self._first_delivery_time

    @property
    def expiration_time(self) -> int | None:
        """Returns the expiration time of the contract if available, None otherwise."""
        return self._expiration_time

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Returns dictionary of all Attributes of the contract."""
        return self._attributes

    def add_attribute(self, name: str, value: Attribute) -> None:
        """Adds a new attribute to the Contract.

        Args:
            name: of the attribute
            value: of the attribute

        Raises:
            ContractError: if attribute already exists, logged on level "ERROR"
        """
        if name in self._attributes:
            raise log_error(self.ContractError(self._ERR_DOUBLE_ATTRIBUTE.format(name)))
        self._attributes[name] = value
        self._notify_data_changed()

    @classmethod
    def from_dict(cls, definitions: dict) -> Contract:
        """Parses contract from given `definitions`.

        Args:
            definitions: dictionary representation of a contract

        Returns:
            new contract

        Raises:
            ContractError: if definitions are incomplete or erroneous, logged on level "ERROR"
        """
        definitions = keys_to_lower(definitions)
        sender_id = Contract._get_or_raise(definitions, Contract.KEY_SENDER, Contract._ERR_MISSING_KEY)
        receiver_id = Contract._get_or_raise(definitions, Contract.KEY_RECEIVER, Contract._ERR_MISSING_KEY)
        product_name = Contract._get_or_raise(definitions, Contract.KEY_PRODUCT, Contract._ERR_MISSING_KEY)

        first_delivery_time = Contract._get_time(definitions, Contract.KEY_FIRST_DELIVERY)
        delivery_interval = Contract._get_interval(definitions)
        expiration_time = Contract._get_time(definitions, Contract.KEY_EXPIRE, mandatory=False)

        contract = cls(sender_id, receiver_id, product_name, delivery_interval, first_delivery_time, expiration_time)
        contract._extract_metadata(definitions)
        contract._init_attributes_from_dict(definitions.get(Contract.KEY_ATTRIBUTES, {}))
        return contract

    @staticmethod
    def _get_or_raise(dictionary: dict, key: str, error_message: str) -> Any:
        """Returns value associated with `key` in given `dictionary`, or raises exception if key or value is missing.

        Args:
            dictionary: to search the key in
            key: to be searched
            error_message: to be logged and included in the raised exception if key is missing

        Returns:
            value associated with given key in given dictionary

         Raises:
             ContractError: if given key is not in given dictionary or value is None, logged on level "ERROR"
        """
        if key not in dictionary or dictionary[key] is None:
            raise log_error(Contract.ContractError(error_message.format(key)))
        return dictionary[key]

    @staticmethod
    @overload
    def _get_time(definitions: dict, key: str) -> int: ...  # noqa: E704

    @staticmethod
    @overload
    def _get_time(definitions: dict, key: str, mandatory: bool) -> int | None: ...  # noqa: E704

    @staticmethod
    def _get_time(definitions: dict, key: str, mandatory: bool = True) -> int | None:
        """Extract time representation value at given key, and, if present, convert to integer, else return None.

        Args:
            definitions: to search given key in
            key: to check for an associated value
            mandatory: if true, also raises an error if key is missing

        Returns:
            None if key is not mandatory/present, else the integer representation of the time value associated with key

        Raises:
            ContractError: if found value could not be converted or mandatory value is missing, logged on level "ERROR"
        """
        if key in definitions:
            value = definitions[key]
            try:
                return FameTime.convert_string_if_is_datetime(value)
            except ConversionError as e:
                raise log_error(Contract.ContractError(Contract._ERR_TIME_CONVERSION.format(key, value))) from e
        if mandatory:
            raise log_error(Contract.ContractError(Contract._ERR_MISSING_KEY.format(key)))
        return None

    @staticmethod
    def _get_interval(definitions: dict) -> int:
        """Extract delivery interval from Contract definition, or raise an error if not present or ill formatted.

        Args:
            definitions: to extract the delivery interval from

        Returns:
            the delivery interval in fame time steps

        Raises:
            ContractError: if delivery interval is not defined or invalid, logged with level "ERROR"
        """
        has_interval = Contract.KEY_INTERVAL in definitions
        has_every = Contract.KEY_EVERY in definitions

        if has_interval and not has_every:
            value = definitions[Contract.KEY_INTERVAL]
            if isinstance(value, int):
                return value
            raise log_error(Contract.ContractError(Contract._ERR_INTERVAL_INVALID.format(value)))
        if has_every and not has_interval:
            value = definitions[Contract.KEY_EVERY]
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                try:
                    return FameTime.convert_text_to_time_span(value)
                except ConversionError as e:
                    raise log_error(
                        Contract.ContractError(Contract._ERR_TIME_CONVERSION.format(Contract.KEY_EVERY, value))
                    ) from e
            raise log_error(Contract.ContractError(Contract._ERR_TIME_CONVERSION.format(Contract.KEY_EVERY, value)))
        raise log_error(
            Contract.ContractError(Contract._ERR_XOR_KEYS.format(Contract.KEY_INTERVAL, Contract.KEY_EVERY))
        )

    def _init_attributes_from_dict(self, attributes: dict[str, Any]) -> None:
        """Resets Contract `attributes` from dict.

        Args:
            attributes: key-value pairs of attributes to be set

        Raises:
            ContractError: if some of provided attributes were already present
        """
        for name, value in attributes.items():
            full_name = f"{type}.{id}{name}"
            self.add_attribute(name, Attribute(full_name, value))

    def _to_dict(self) -> dict:
        """Serializes the Contract content to a dict."""
        result = {
            self.KEY_SENDER: self.sender_id,
            self.KEY_RECEIVER: self.receiver_id,
            self.KEY_PRODUCT: self.product_name,
            self.KEY_FIRST_DELIVERY: self.first_delivery_time,
            self.KEY_INTERVAL: self.delivery_interval,
        }

        if self.expiration_time is not None:
            result[self.KEY_EXPIRE] = self.expiration_time

        if len(self.attributes) > 0:
            result[self.KEY_ATTRIBUTES] = {name: value.to_dict() for name, value in self.attributes.items()}
        return result

    @staticmethod
    def split_contract_definitions(multi_definition: dict) -> list[dict]:
        """Split given M:N `multi_definition` of contracts to multiple 1:1 contracts.

        Splits given dictionary of contracts with potentially more than ore sender and/or receiver into a list
        of individual contract definitions with one sender and one receiver.

        Args:
            multi_definition: contract definitions with potentially more than ore sender and/or receiver

        Returns:
            list of contract definitions with exactly one sender and receiver

        Raises:
            ContractError: if multi_definition is incomplete or erroneous, logged on level "ERROR"
        """
        contracts = []
        base_data = {}
        multi_definition = keys_to_lower(multi_definition)
        for key in [
            Contract.KEY_PRODUCT,
            Contract.KEY_FIRST_DELIVERY,
            Contract.KEY_INTERVAL,
            Contract.KEY_EXPIRE,
            Contract.KEY_METADATA,
            Contract.KEY_ATTRIBUTES,
            Contract.KEY_EVERY,
        ]:
            if key in multi_definition:
                base_data[key] = multi_definition[key]
        sender_value = Contract._get_or_raise(multi_definition, Contract.KEY_SENDER, Contract._ERR_MISSING_KEY)
        senders = Contract._unpack_list(sender_value)
        receiver_value = Contract._get_or_raise(multi_definition, Contract.KEY_RECEIVER, Contract._ERR_MISSING_KEY)
        receivers = Contract._unpack_list(receiver_value)
        if len(senders) > 1 and len(receivers) == 1:
            for index, sender in enumerate(senders):
                contracts.append(Contract._copy_contract(sender, receivers[0], base_data))
        elif len(senders) == 1 and len(receivers) > 1:
            for index, receiver in enumerate(receivers):
                contracts.append(Contract._copy_contract(senders[0], receiver, base_data))
        elif len(senders) == len(receivers):
            for index in range(len(senders)):  # pylint: disable=consider-using-enumerate
                contracts.append(Contract._copy_contract(senders[index], receivers[index], base_data))
        else:
            raise log_error(Contract.ContractError(Contract._ERR_MULTI_CONTRACT_CORRUPT.format(senders, receivers)))
        return contracts

    @staticmethod
    def _unpack_list(obj: Any | list) -> list[Any]:
        """Returns the given value as a flat list - unpacks potential nested list(s)"""
        if isinstance(obj, list):
            return [item for element in obj for item in Contract._unpack_list(element)]
        return [obj]

    @staticmethod
    def _copy_contract(sender: int, receiver: int, base_data: dict) -> dict:
        """Returns a new contract definition dictionary, with given `sender` and `receiver` and copied `base_data`."""
        contract = {
            Contract.KEY_SENDER: sender,
            Contract.KEY_RECEIVER: receiver,
        }
        contract.update(base_data)
        return contract
