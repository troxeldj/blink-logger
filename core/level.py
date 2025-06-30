from enum import Enum, auto


class LoggingLevel(Enum):
  DEBUG = auto()
  INFO = auto()
  WARNING = auto()
  ERROR = auto()
  CRITICAL = auto()

  def __str__(self):
    return self.name

  def __repr__(self):
    return f"LoggingLevel.{self.name}"

  def __eq__(self, other):
    if isinstance(other, LoggingLevel):
      return self.value == other.value
    return NotImplemented

  def __ne__(self, other):
    if isinstance(other, LoggingLevel):
      return self.value != other.value
    return NotImplemented

  def __lt__(self, other):
    if isinstance(other, LoggingLevel):
      return self.value < other.value
    return NotImplemented

  def __le__(self, other):
    if isinstance(other, LoggingLevel):
      return self.value <= other.value
    return NotImplemented

  def __gt__(self, other):
    if isinstance(other, LoggingLevel):
      return self.value > other.value
    return NotImplemented

  def __ge__(self, other):
    if isinstance(other, LoggingLevel):
      return self.value >= other.value
    return NotImplemented
