from .level import LoggingLevel
from datetime import datetime


class LogRecord:
    """
    A class representing a log record with a specific logging level, message, source, and metadata.
    It includes a 	timestamp that can be set when the record is created or later.

    Parameters:
    - level (LoggingLevel): The logging level of the record (e.g., DEBUG
    , INFO, WARNING, ERROR, CRITICAL).
    - message (str): The log message.
    - source (Optional[str]): The source of the log record, such as the name
    of the module or function generating the log. Defaults to None.
    - metadata (Optional[Dict[str, Any]]): Additional metadata associated with the log
    record, such as context information. Defaults to None.
    - timestamp (datetime): The timestamp of the log record, set to the current time
    when the record is created. Defaults to the current time.
    """

    def __init__(self, level: LoggingLevel, message: str, source=None, metadata=None):
        self.level = level
        self.message = message
        self.source = source
        self.metadata = metadata if metadata is not None else {}
        # set timestamp to current time
        self.timestamp = datetime.now()

    def set_timestamp(self, timestamp: datetime):
        """
        Set the timestamp for the log record.
        :param timestamp: A datetime object representing the timestamp to set.
        """
        self.timestamp = timestamp
