from enum import Enum


class ConsoleColor(Enum):
  RESET = "\033[0m"
  RED = "\033[31m"
  GREEN = "\033[32m"
  YELLOW = "\033[33m"
  BLUE = "\033[34m"
  MAGENTA = "\033[35m"
  CYAN = "\033[36m"
  WHITE = "\033[37m"
  DEFAULT = "\033[39m"

  def __str__(self):
    return self.value

  def __repr__(self):
    return f"<ConsoleColor: {self.name} ({self.value})>"
