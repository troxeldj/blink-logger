from abc import ABC, abstractmethod
from core.record import LogRecord
from utils.dec import throws
from utils.interfaces import JsonSerializable
from typing import override


class BaseFormatter(JsonSerializable):

    @override
    @classmethod
    def from_dict(cls, data: dict) -> "BaseFormatter":
        """
        Create an instance of BaseFormatter from a dictionary representation.

        Args:
                data (dict): The dictionary representation of the formatter.

        Returns:
                BaseFormatter: An instance of BaseFormatter.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @override
    @classmethod
    def to_dict(self) -> dict:
        """
        Convert the instance to a dictionary representation.

        Returns:
                dict: The dictionary representation of the formatter.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @throws(NotImplementedError)
    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Format a log record into the desired output format"""
        raise NotImplementedError("Subclasses must implement this method")
