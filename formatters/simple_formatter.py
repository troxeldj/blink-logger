from formatters.base_formatter import BaseFormatter
from core.record import LogRecord
from typing import Optional


class SimpleFormatter(BaseFormatter):
    """Simple formatter for log records that outputs a basic string representation."""

    def __init__(self):
        super().__init__()

    def format(self, record: LogRecord) -> str:
        """Formats the log record into a simple string."""
        # Basic format: "timestamp - level - message"
        timestamp = record.timestamp.isoformat() if record.timestamp else "N/A"
        level = (
            record.level.name if hasattr(record.level, "name") else str(record.level)
        )
        message = record.message or "No message provided"
        return f"[{timestamp} {level}]: {message}"

    def __repr__(self):
        return f"<SimpleFormatter: {self.__class__.__name__}>"

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleFormatter":
        """Creates an instance of SimpleFormatter from a dictionary representation.

        Args:
            data (dict): The dictionary representation of the formatter.

        Returns:
            SimpleFormatter: An instance of SimpleFormatter.
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        return cls()

    @classmethod
    def to_dict(cls) -> dict:
        """Converts the instance to a dictionary representation.

        Returns:
            dict: The dictionary representation of the formatter.
        """
        return {"type": "SimpleFormatter"}
