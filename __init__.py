"""
blink-logger: A custom Python logging library built from scratch.

A modern logging library with filtered logging, colored output, multiple appenders,
builder patterns, and global logger management.
"""

__version__ = "0.1.0"
__author__ = "Dillon"

# Core Components
from core.logger import Logger
from core.level import LoggingLevel
from core.record import LogRecord
from core.color import ConsoleColor

# Builders
from builders.logger_builder import LoggerBuilder

# Appenders
from appenders.base_appender import BaseAppender
from appenders.console_appender import ConsoleAppender, ColoredConsoleAppender
from appenders.file_appender import FileAppender
from appenders.composite_appender import CompositeAppender

# Formatters
from formatters.base_formatter import BaseFormatter
from formatters.simple_formatter import SimpleFormatter
from formatters.json_formatter import JSONFormatter

# Filters
from filters.base_filter import BaseFilter
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter

# Managers
from managers.log_manager import LogManager
from managers.global_manager import GlobalManager

# Decorators
from decorators import (
  logged, timed, performance_monitor, debug_logged, error_handler
)

# Global logger access
def get_global_logger() -> Logger:
  """Get the global logger instance for easy access."""
  return GlobalManager.get_global_logger()

# Public API exports
__all__ = [
  # Core
  "Logger",
  "LoggingLevel", 
  "LogRecord",
  "ConsoleColor",
  
  # Builders
  "LoggerBuilder",
  
  # Appenders
  "BaseAppender",
  "ConsoleAppender",
  "ColoredConsoleAppender", 
  "FileAppender",
  "CompositeAppender",
  
  # Formatters
  "BaseFormatter",
  "SimpleFormatter",
  "JSONFormatter",
  
  # Filters
  "BaseFilter",
  "KeywordFilter",
  "LevelFilter",
  
  # Managers
  "LogManager",
  "GlobalManager",
  
  # Decorators
  "logged",
  "timed", 
  "performance_monitor",
  "debug_logged",
  "error_handler",
  
  # Global access
  "get_global_logger",
]

# Convenience functions for quick setup
def get_logger(name: str) -> Logger:
  """
  Get a logger instance from the global manager.
  
  Args:
    name: The name of the logger to retrieve
    
  Returns:
    Logger instance
    
  Raises:
    KeyError: If logger with given name doesn't exist
  """
  return GlobalManager.get_instance().get_logger(name)


def create_simple_logger(name: str, level: LoggingLevel = LoggingLevel.INFO) -> Logger:
  """
  Create a simple logger with console output.
  
  Args:
    name: Name for the logger
    level: Logging level (default: INFO)
    
  Returns:
    Configured Logger instance
  """
  return (LoggerBuilder()
      .set_name(name)
      .set_level(level)
      .add_appender(ConsoleAppender(formatter=SimpleFormatter()))
      .build())


def create_colored_logger(name: str, 
             level: LoggingLevel = LoggingLevel.INFO,
             color: ConsoleColor = ConsoleColor.DEFAULT) -> Logger:
  """
  Create a logger with colored console output.
  
  Args:
    name: Name for the logger
    level: Logging level (default: INFO)
    color: Console color (default: DEFAULT)
    
  Returns:
    Configured Logger instance with colored output
  """
  return (LoggerBuilder()
      .set_name(name)
      .set_level(level)
      .add_appender(ColoredConsoleAppender(formatter=SimpleFormatter(), color=color))
      .build())
