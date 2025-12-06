# app/db/serializers.py
import json
import pickle
from abc import ABC, abstractmethod
from typing import Any


class Serializer(ABC):
    """
    Abstract base class for object serialization strategies.

    The class defines the interface for converting Python objects to bytes
    and vice versa.

    Notes
    -----
    The implementation should ensure that `deserialize(serialize(obj))`
    returns an equivalent object to the original input.
    """

    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        """
        Convert a Python object into a byte representation.

        Parameters
        ----------
        obj : Any
            The Python object to serialize.

        Returns
        -------
        bytes
            Byte representation of the object.
        """
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """
        Reconstruct a Python object from its byte representation.

        Parameters
        ----------
        data : bytes
            Byte representation of the serialized object.

        Returns
        -------
        Any
            The deserialized Python object.
        """
        pass


class JsonSerializer(Serializer):
    """
    JSON-based serialization strategy.

    Converts Python objects to JSON-formatted UTF-8 bytes and back.
    Only supports JSON-serializable types: dict, list, str, int, float, bool, None.
    """

    def serialize(self, obj: Any) -> bytes:
        """
        Convert a Python object to JSON-formatted UTF-8 bytes.

        Parameters
        ----------
        obj : Any
            A JSON-serializable Python object.

        Returns
        -------
        bytes
            UTF-8 encoded JSON representation of the object.

        Raises
        ------
        TypeError
            If the object contains non-JSON-serializable types.
        """

        return json.dumps(obj).encode('utf-8')

    def deserialize(self, data: bytes) -> Any:
        """
        Reconstruct a Python object from JSON-formatted bytes.

        Parameters
        ----------
        data : bytes
            UTF-8 encoded JSON data.

        Returns
        -------
        Any
            The deserialized Python object.

        Raises
        ------
        json.JSONDecodeError
            If the input is not valid JSON.
        """

        return json.loads(data.decode('utf-8'))


class PickleSerializer(Serializer):
    """
    Pickle-based serialization strategy.

    Converts arbitrary Python objects to pickle byte streams and back.
    Supports complex types including custom classes, nested objects, and closures.
    """

    def serialize(self, obj: Any) -> bytes:
        """
        Convert a Python object to a pickle byte stream.

        Parameters
        ----------
        obj : Any
            Any picklable Python object.

        Returns
        -------
        bytes
            Pickle-encoded byte representation of the object.

        Raises
        ------
        pickle.PicklingError
            If the object cannot be pickled (e.g., lambda, open file, etc.).
        """

        return pickle.dumps(obj)

    def deserialize(self, data: bytes) -> Any:
        """
        Reconstruct a Python object from a pickle byte stream.

        Parameters
        ----------
        data : bytes
            Pickle-encoded byte stream.

        Returns
        -------
        Any
            The deserialized Python object.

        Raises
        ------
        pickle.UnpicklingError
            If the data is corrupted or not a valid pickle stream.
        """

        return pickle.loads(data)