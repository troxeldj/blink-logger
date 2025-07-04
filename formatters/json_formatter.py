from formatters.base_formatter import BaseFormatter
from core.record import LogRecord
from core.level import LoggingLevel
from typing import Optional, override
import json


class JSONFormatter(BaseFormatter):
    def __init__(self):
        """Initializes the JSON formatter."""
        super().__init__()

    def format(self, record: LogRecord) -> str:
        """Formats a log record into a JSON string.

        Args:
            record (LogRecord): The log record to format.

        Returns:
            str: The formatted log record as a JSON string.
        """
        log_data = {
            "message": record.message,
            "level": (
                record.level.name
                if isinstance(record.level, LoggingLevel)
                else str(record.level)
            ),
            "timestamp": record.timestamp.isoformat(),
        }

        if record.source:
            log_data["source"] = record.source

        if record.metadata:
            log_data.update(record.metadata)

        return json.dumps(log_data, default=str)

    @classmethod
    def from_dict(cls, data: dict) -> "JSONFormatter":
        """Creates an instance of JSONFormatter from a dictionary representation.

        Args:
            data (dict): The dictionary representation of the formatter.

        Returns:
            JSONFormatter: An instance of JSONFormatter.
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        if data.get("type") != "JSONFormatter":
            raise ValueError("Invalid formatter type. Expected 'JSONFormatter'.")
        return cls()

    @override
    def to_dict(self) -> dict:
        """Converts the instance to a dictionary representation.

        Returns:
            dict: The dictionary representation of the formatter.
        """
        return {"type": "JSONFormatter"}
