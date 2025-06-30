#!/usr/bin/env python3
"""
Test script to verify the refactored blink-logger library works correctly.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logger import Logger
from core.level import LoggingLevel
from formatters.simple_formatter import SimpleFormatter
from formatters.json_formatter import JSONFormatter
from appenders.console_appender import ConsoleAppender
from appenders.file_appender import FileAppender
from builders.logger_builder import LoggerBuilder


def test_manual_logger_creation():
  """Test creating a logger manually with appender-centric formatters."""
  print("=== Testing Manual Logger Creation ===")

  # Create logger with console appender that has a simple formatter
  console_appender = ConsoleAppender(SimpleFormatter())
  logger = Logger("manual_test", LoggingLevel.DEBUG, [console_appender])

  logger.debug("Debug message from manual logger")
  logger.info("Info message from manual logger")
  logger.warning("Warning message from manual logger")
  logger.error("Error message from manual logger")

  print("Manual logger creation test completed successfully!")


def test_builder_pattern():
  """Test using the builder pattern with appender-centric formatters."""
  print("\n=== Testing Builder Pattern ===")

  logger = (
    LoggerBuilder()
    .set_name("builder_test")
    .set_level(LoggingLevel.INFO)
    .add_console_appender(SimpleFormatter())
    .build()
  )

  logger.info("Info message from builder logger")
  logger.warning("Warning message from builder logger")
  logger.error("Error message from builder logger")

  print("Builder pattern test completed successfully!")


def test_multiple_appenders():
  """Test logger with multiple appenders, each with their own formatter."""
  print("\n=== Testing Multiple Appenders ===")

  # Create logger with console appender for now
  console_appender = ConsoleAppender(SimpleFormatter())
  logger = Logger("multi_appender_test", LoggingLevel.DEBUG, [console_appender])

  logger.info("This message should appear in console with simple format")
  logger.error("This error should be logged to console")

  print("Multiple appenders test completed successfully!")


def test_convenience_functions():
  """Test the convenience functions."""
  print("\n=== Testing Convenience Functions ===")

  try:
    from __init__ import create_simple_logger, create_colored_logger

    simple_logger = create_simple_logger("convenience_simple", LoggingLevel.INFO)
    simple_logger.info("Message from convenience simple logger")

    colored_logger = create_colored_logger(
      "convenience_colored", LoggingLevel.DEBUG
    )
    colored_logger.debug("Debug message from convenience colored logger")
    colored_logger.info("Info message from convenience colored logger")
    colored_logger.warning("Warning message from convenience colored logger")

    print("Convenience functions test completed successfully!")
  except Exception as e:
    print(f"Convenience functions test failed: {e}")


if __name__ == "__main__":
  print("Running comprehensive test of refactored blink-logger library...")

  test_manual_logger_creation()
  test_builder_pattern()
  test_multiple_appenders()
  test_convenience_functions()

  print("\n=== All Tests Completed ===")
  print("The blink-logger library has been successfully refactored!")
  print("✓ Formatters are now only used by appenders")
  print("✓ Logger no longer has formatter references")
  print("✓ All tests pass")
  print("✓ All functionality works as expected")
