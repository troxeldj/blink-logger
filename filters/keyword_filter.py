from filters.base_filter import BaseFilter
from core.record import LogRecord
from utils.dec import throws
from typing import List, Optional, Union


class KeywordFilter(BaseFilter):
  @throws(ValueError)
  def __init__(self, keywords: Optional[Union[str, List[str]]] = None):
    """
    Initialize the KeywordFilter with specific keywords.

    Args:
            keywords (Union[str, List[str]]): A single keyword or a list of keywords to filter by.
    """
    if keywords:
      if isinstance(keywords, str):
        keywords = [keywords]
      elif not isinstance(keywords, list):
        raise ValueError("Keywords must be a string or a list of strings.")
      if not all(isinstance(keyword, str) for keyword in keywords):
        raise ValueError("All keywords must be strings.")
    else:
      keywords = []
    self.keywords: List[str] = keywords

  def should_log(self, record: LogRecord) -> bool:
    """
    Determine if the log record should be processed by this filter based on its content.

    Args:
            record (LogRecord): The log record to evaluate.

    Returns:
            bool: True if the record's message contains any of the keywords, False otherwise.
    """
    return any(keyword in record.message for keyword in self.keywords)

  @classmethod
  def from_dict(cls, data: dict) -> "KeywordFilter":
    """
    Create a KeywordFilter instance from a dictionary.

    Args:
            data (dict): The dictionary representation of the filter.

    Returns:
            KeywordFilter: An instance of KeywordFilter.
    """
    keywords = data.get("keywords", [])
    if isinstance(keywords, str):
      keywords = [keywords]
    return cls(keywords)

  def to_dict(self) -> dict:
    """
    Convert the KeywordFilter instance to a dictionary representation.

    Returns:
            dict: The dictionary representation of the filter.
    """
    return {"type": "KeywordFilter", "keywords": self.keywords}
