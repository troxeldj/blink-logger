from core.record import LogRecord
from abc import ABC, abstractmethod
from utils.interfaces import JsonSerializable


class BaseFilter(ABC, JsonSerializable):
    @abstractmethod
    def should_log(self, record: LogRecord) -> bool:
        """Determine if the log record should be processed by this filter."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "BaseFilter":
        raise NotImplementedError("Subclasses must implement from_dict method")

    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError("Subclasses must implement to_dict method")
