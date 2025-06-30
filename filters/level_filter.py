from filters.base_filter import BaseFilter
from core.record import LogRecord
from core.level import LoggingLevel
from utils.dec import throws


class LevelFilter(BaseFilter):
  @throws(ValueError)
  def __init__(self, level: LoggingLevel):
    """
    Initialize the LevelFilter with a specific logging level.

    Args:
        level (LoggingLevel): The logging level to filter by.
    """
    if not level or not isinstance(level, LoggingLevel):
      raise ValueError(
        "Invalid logging level provided. Must be an instance of LoggingLevel."
      )
    self.level: LoggingLevel = level

  def should_log(self, record: LogRecord) -> bool:
    """
    Determine if the log record should be processed by this filter based on its level.

    Args:
        record (LogRecord): The log record to evaluate.

    Returns:
        bool: True if the record's level is greater than or equal to the filter's level, False otherwise.
    """
    return record.level >= self.level

  @classmethod
  def from_dict(cls, data: dict) -> "LevelFilter":
    """
    Create a LevelFilter instance from a dictionary.

    Args:
        data (dict): Dictionary containing 'level' key.

    Returns:
        LevelFilter: An instance of LevelFilter.
    """
    if "level" not in data:
      raise ValueError("Dictionary must contain 'level' key")

    level_str = data["level"]
    if isinstance(level_str, str):
      level = LoggingLevel[level_str.upper()]
    elif isinstance(level_str, LoggingLevel):
      level = level_str
    else:
      raise ValueError(f"Invalid level type: {type(level_str)}")

    return cls(level)

  def to_dict(self) -> dict:
    """
    Convert the LevelFilter instance to a dictionary.

    Returns:
        dict: Dictionary representation of the filter.
    """
    return {"type": "LevelFilter", "level": self.level.name}
