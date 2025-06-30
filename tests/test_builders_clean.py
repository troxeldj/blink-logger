#!/usr/bin/env python3
# mypy: ignore-errors
"""
Updated test suite for LoggerBuilder class focusing on the new appender-centric design.

This module tests the builder pattern implementation for constructing Logger instances,
without the need for formatters since they are now handled by appenders.
"""

import pytest
import sys
import os

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builders.logger_builder import LoggerBuilder
from core.logger import Logger
from core.level import LoggingLevel
from formatters.simple_formatter import SimpleFormatter
from appenders.console_appender import ConsoleAppender
from appenders.file_appender import FileAppender
from appenders.composite_appender import CompositeAppender
from core.record import LogRecord
from managers.global_manager import GlobalManager


@pytest.fixture(autouse=True)
def clean_global_manager():
  """Clean the GlobalManager before each test to avoid conflicts."""
  GlobalManager.get_instance().clear_loggers()
  yield
  GlobalManager.get_instance().clear_loggers()


class TestLoggerBuilderBasics:
  """Test basic LoggerBuilder functionality and initialization."""

  def test_builder_initialization(self):
    """Test that LoggerBuilder initializes with correct default values."""
    builder = LoggerBuilder()

    assert builder.name is None
    assert builder.level is None
    assert builder.appenders == []
    assert isinstance(builder.appenders, list)
    # Verify formatter functionality removed
    assert not hasattr(builder, "formatter")

  def test_builder_is_reusable(self):
    """Test that a new builder instance starts fresh."""
    builder1 = LoggerBuilder()
    builder1.set_name("test1")

    builder2 = LoggerBuilder()
    assert builder2.name is None
    assert builder2.name != builder1.name


class TestLoggerBuilderSetters:
  """Test LoggerBuilder setter methods and validation."""

  def test_set_name_valid(self):
    """Test setting valid logger names."""
    builder = LoggerBuilder()

    # Test simple name
    result = builder.set_name("TestLogger")
    assert builder.name == "TestLogger"
    assert result is builder  # Test method chaining

    # Test name with spaces and special characters
    builder.set_name("Test Logger 123 !@#")
    assert builder.name == "Test Logger 123 !@#"

    # Test empty string (should be allowed)
    builder.set_name("")
    assert builder.name == ""

  def test_set_name_invalid(self):
    """Test setting invalid logger names raises TypeError."""
    builder = LoggerBuilder()

    invalid_names = [None, 123, [], {}, set(), object()]

    for invalid_name in invalid_names:
      with pytest.raises(TypeError, match="name must be a string"):
        builder.set_name(invalid_name)

  def test_set_level_valid(self):
    """Test setting valid logging levels."""
    builder = LoggerBuilder()

    # Test all valid logging levels
    levels = [
      LoggingLevel.DEBUG,
      LoggingLevel.INFO,
      LoggingLevel.WARNING,
      LoggingLevel.ERROR,
      LoggingLevel.CRITICAL,
    ]

    for level in levels:
      result = builder.set_level(level)
      assert builder.level == level
      assert result is builder  # Test method chaining

  def test_set_level_invalid(self):
    """Test setting invalid logging levels raises TypeError."""
    builder = LoggerBuilder()

    invalid_levels = [None, "INFO", 1, [], {}, set(), object()]

    for invalid_level in invalid_levels:
      with pytest.raises(
        TypeError, match="level must be an instance of LoggingLevel"
      ):
        builder.set_level(invalid_level)

  def test_add_appender_valid(self):
    """Test adding valid appenders."""
    builder = LoggerBuilder()

    # Test ConsoleAppender with formatter
    console_appender = ConsoleAppender(formatter=SimpleFormatter())
    result = builder.add_appender(console_appender)
    assert console_appender in builder.appenders
    assert len(builder.appenders) == 1
    assert result is builder  # Test method chaining

    # Test FileAppender with formatter
    file_appender = FileAppender("test.log", formatter=SimpleFormatter())
    builder.add_appender(file_appender)
    assert file_appender in builder.appenders
    assert len(builder.appenders) == 2

  def test_add_appender_invalid(self):
    """Test adding invalid appender types raises TypeError."""
    builder = LoggerBuilder()

    invalid_appenders = [None, "appender", 123, [], {}, set(), object()]

    for invalid_appender in invalid_appenders:
      with pytest.raises(
        TypeError, match="appender must be an instance of BaseAppender"
      ):
        builder.add_appender(invalid_appender)


class TestLoggerBuilderChaining:
  """Test LoggerBuilder method chaining functionality."""

  def test_full_chain_construction(self):
    """Test complete logger construction using method chaining."""
    console_appender = ConsoleAppender(formatter=SimpleFormatter())
    file_appender = FileAppender("test.log", formatter=SimpleFormatter())

    logger = (
      LoggerBuilder()
      .set_name("ChainedLogger")
      .set_level(LoggingLevel.DEBUG)
      .add_appender(console_appender)
      .add_appender(file_appender)
      .build()
    )

    assert isinstance(logger, Logger)
    assert logger.get_name() == "ChainedLogger"
    assert logger.get_level() == LoggingLevel.DEBUG
    assert len(logger.get_appenders()) == 2
    assert console_appender in logger.get_appenders()
    assert file_appender in logger.get_appenders()

  def test_partial_chain_construction(self):
    """Test construction with partial method chaining."""
    builder = LoggerBuilder()

    # Chain some methods
    builder.set_name("PartialChain").set_level(LoggingLevel.INFO)

    # Add remaining components separately
    builder.add_appender(ConsoleAppender(formatter=SimpleFormatter()))

    logger = builder.build()

    assert isinstance(logger, Logger)
    assert logger.get_name() == "PartialChain"
    assert logger.get_level() == LoggingLevel.INFO
    assert len(logger.get_appenders()) == 1

  def test_order_independence(self):
    """Test that method call order doesn't affect final result."""
    appender1 = ConsoleAppender(formatter=SimpleFormatter())
    appender2 = ConsoleAppender(formatter=SimpleFormatter())

    # Build logger with one order
    logger1 = (
      LoggerBuilder()
      .add_appender(appender1)
      .set_name("OrderTest1")
      .set_level(LoggingLevel.WARNING)
      .build()
    )

    # Build logger with different order
    logger2 = (
      LoggerBuilder()
      .set_level(LoggingLevel.WARNING)
      .set_name("OrderTest2")
      .add_appender(appender2)
      .build()
    )

    assert logger1.get_name() == "OrderTest1"
    assert logger2.get_name() == "OrderTest2"
    assert logger1.get_level() == logger2.get_level()
    assert len(logger1.get_appenders()) == len(logger2.get_appenders())


class TestLoggerBuilderBuild:
  """Test LoggerBuilder build functionality and validation."""

  def test_build_success_minimal(self):
    """Test successful build with minimal configuration."""
    appender = ConsoleAppender(formatter=SimpleFormatter())

    logger = (
      LoggerBuilder().set_name("MinimalLogger").add_appender(appender).build()
    )

    assert isinstance(logger, Logger)
    assert logger.get_name() == "MinimalLogger"
    assert logger.get_level() == LoggingLevel.INFO  # Default level
    assert len(logger.get_appenders()) == 1

  def test_build_success_complete(self):
    """Test successful build with complete configuration."""
    appender = ConsoleAppender(formatter=SimpleFormatter())

    logger = (
      LoggerBuilder()
      .set_name("CompleteLogger")
      .set_level(LoggingLevel.ERROR)
      .add_appender(appender)
      .build()
    )

    assert isinstance(logger, Logger)
    assert logger.get_name() == "CompleteLogger"
    assert logger.get_level() == LoggingLevel.ERROR
    assert len(logger.get_appenders()) == 1

  def test_build_missing_name(self):
    """Test build fails when name is missing."""
    builder = LoggerBuilder()
    builder.add_appender(ConsoleAppender(formatter=SimpleFormatter()))

    with pytest.raises(ValueError, match="Logger name must be set"):
      builder.build()

  def test_build_missing_appenders(self):
    """Test build fails when no appenders are provided."""
    builder = LoggerBuilder()
    builder.set_name("TestLogger")

    with pytest.raises(ValueError, match="At least one appender must be added"):
      builder.build()

  def test_build_empty_name_not_allowed(self):
    """Test build fails with empty name."""
    builder = LoggerBuilder()
    builder.set_name("")
    builder.add_appender(ConsoleAppender(formatter=SimpleFormatter()))

    with pytest.raises(ValueError, match="Logger name must be set"):
      builder.build()


class TestLoggerBuilderEdgeCases:
  """Test LoggerBuilder edge cases and complex scenarios."""

  def test_multiple_builds_from_same_builder(self):
    """Test that multiple builds from same builder with same name raises error."""
    builder = (
      LoggerBuilder()
      .set_name("MultiBuilder")
      .add_appender(ConsoleAppender(formatter=SimpleFormatter()))
    )

    logger1 = builder.build()

    # Attempting to build another logger with the same name should raise an error
    with pytest.raises(
      ValueError, match="A logger with the name 'MultiBuilder' already exists"
    ):
      logger2 = builder.build()

  def test_builder_modification_after_build(self):
    """Test that modifying builder after build affects new loggers."""
    original_appender = ConsoleAppender(formatter=SimpleFormatter())
    builder = LoggerBuilder().set_name("ModifyTest").add_appender(original_appender)

    logger1 = builder.build()

    # Add another appender to builder
    additional_appender = FileAppender("test.log", formatter=SimpleFormatter())
    builder.add_appender(additional_appender)

    # Change the name for the second logger to avoid conflicts
    builder.set_name("ModifyTest2")
    logger2 = builder.build()

    # First logger should still have only one appender
    assert len(logger1.get_appenders()) == 1
    # Second logger should have both appenders
    assert len(logger2.get_appenders()) == 2

  def test_composite_appender_integration(self):
    """Test builder works with CompositeAppender."""
    console_appender = ConsoleAppender(formatter=SimpleFormatter())
    file_appender = FileAppender("test.log", formatter=SimpleFormatter())
    composite_appender = CompositeAppender(
      appenders=[console_appender, file_appender]
    )

    logger = (
      LoggerBuilder()
      .set_name("CompositeTest")
      .add_appender(composite_appender)
      .build()
    )

    assert isinstance(logger, Logger)
    assert len(logger.get_appenders()) == 1
    assert isinstance(logger.get_appenders()[0], CompositeAppender)

  def test_builder_state_isolation(self):
    """Test that different builder instances don't affect each other."""
    builder1 = LoggerBuilder().set_name("Builder1")
    builder2 = LoggerBuilder().set_name("Builder2")

    # Verify they are independent
    assert builder1.name != builder2.name
    assert len(builder1.appenders) == 0
    assert len(builder2.appenders) == 0

    # Modify one
    builder1.add_appender(ConsoleAppender(formatter=SimpleFormatter()))

    # Other should be unaffected
    assert len(builder2.appenders) == 0


class TestLoggerBuilderIntegration:
  """Test LoggerBuilder integration with Logger functionality."""

  def test_built_logger_logging_functionality(self):
    """Test that built logger can actually log messages."""
    import io
    from unittest.mock import patch

    appender = ConsoleAppender(formatter=SimpleFormatter())
    logger = (
      LoggerBuilder()
      .set_name("TestLogger")
      .set_level(LoggingLevel.INFO)
      .add_appender(appender)
      .build()
    )

    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
      logger.log(LoggingLevel.INFO, "Test message")
      output = mock_stdout.getvalue()
      assert "Test message" in output
      assert "INFO" in output

  def test_built_logger_level_filtering(self):
    """Test that built logger respects level filtering."""
    logger = (
      LoggerBuilder()
      .set_name("LevelTest")
      .set_level(LoggingLevel.WARNING)
      .add_appender(ConsoleAppender(formatter=SimpleFormatter()))
      .build()
    )

    # Verify level is set correctly
    assert logger.get_level() == LoggingLevel.WARNING

    # Logger should filter out messages below WARNING level
    assert logger.get_level().value >= LoggingLevel.WARNING.value

  def test_built_logger_appender_management(self):
    """Test that built logger properly manages appenders."""
    initial_appender = ConsoleAppender(formatter=SimpleFormatter())

    logger = (
      LoggerBuilder()
      .set_name("AppenderTest")
      .add_appender(initial_appender)
      .build()
    )

    # Test that logger has the appender
    assert len(logger.get_appenders()) == 1
    assert initial_appender in logger.get_appenders()

    # Test that we can add more appenders to the built logger
    additional_appender = FileAppender(
      "additional.log", formatter=SimpleFormatter()
    )
    logger.add_appender(additional_appender)

    assert len(logger.get_appenders()) == 2
    assert additional_appender in logger.get_appenders()


class TestLoggerBuilderPerformance:
  """Test LoggerBuilder performance characteristics."""

  def test_large_number_of_appenders(self):
    """Test builder with many appenders."""
    builder = LoggerBuilder().set_name("ManyAppenders")

    # Add many appenders
    for i in range(50):
      builder.add_appender(ConsoleAppender(formatter=SimpleFormatter()))

    logger = builder.build()

    assert isinstance(logger, Logger)
    assert len(logger.get_appenders()) == 50

  def test_builder_reuse_performance(self):
    """Test performance of reusing builder for multiple logger creation."""
    base_builder = LoggerBuilder().add_appender(
      ConsoleAppender(formatter=SimpleFormatter())
    )

    loggers = []
    for i in range(10):
      logger = base_builder.set_name(f"Logger{i}").build()
      loggers.append(logger)

    # All should be valid
    assert len(loggers) == 10
    assert all(isinstance(logger, Logger) for logger in loggers)


def run_manual_tests():
  """Manual test runner for verification."""
  print("Running LoggerBuilder tests...")

  # Test basic construction
  logger = (
    LoggerBuilder()
    .set_name("ManualTest")
    .set_level(LoggingLevel.DEBUG)
    .add_appender(ConsoleAppender(formatter=SimpleFormatter()))
    .build()
  )

  logger.log(LoggingLevel.INFO, "Manual test successful!")
  print("✅ Manual test passed!")


if __name__ == "__main__":
  run_manual_tests()
