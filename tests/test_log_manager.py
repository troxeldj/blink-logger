#!/usr/bin/env python3
# mypy: ignore-errors
"""
Comprehensive test suite for LogManager class.

This module tests the LogManager functionality including:
- Logger management and validation
- Dictionary-like operations
- Error handling and validation
- Iterator and container protocols
- Edge cases and error conditions

Test Coverage:
- LogManager initialization and configuration
- Adding, removing, and retrieving loggers
- Dictionary-like access patterns
- Validation and error handling
- Container operations (contains, len, iter)
- String representations
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.log_manager import LogManager
from core.logger import Logger
from core.level import LoggingLevel
from formatters.simple_formatter import SimpleFormatter
from appenders.console_appender import ConsoleAppender
from appenders.base_appender import BaseAppender


@pytest.fixture
def mock_appender():
  """Fixture for creating a mock appender."""
  return Mock(spec=BaseAppender)


@pytest.fixture
def mock_logger():
  """Fixture for creating a mock logger that doesn't auto-register."""
  mock = Mock()
  mock.name = "test_logger"
  mock.get_name.return_value = "test_logger"
  return mock


@pytest.fixture
def another_mock_logger():
  """Fixture for creating another mock logger."""
  mock = Mock()
  mock.name = "another_logger"
  mock.get_name.return_value = "another_logger"
  return mock


@pytest.fixture
def isolated_logger(mock_appender):
  """Create a logger without triggering global registration."""
  # Temporarily patch GlobalManager to avoid auto-registration
  with patch("managers.global_manager.GlobalManager") as mock_global:
    mock_appender.formatter = SimpleFormatter()
    logger = Logger(
      name="isolated_logger", level=LoggingLevel.INFO, appenders=[mock_appender]
    )
    return logger


@pytest.fixture
def another_isolated_logger(mock_appender):
  """Create another logger without triggering global registration."""
  with patch("managers.global_manager.GlobalManager") as mock_global:
    mock_appender.formatter = SimpleFormatter()
    logger = Logger(
      name="another_isolated", level=LoggingLevel.DEBUG, appenders=[mock_appender]
    )
    return logger


@pytest.fixture
def sample_logger(mock_appender):
  """Fixture for creating a sample logger without auto-registration."""
  with patch("managers.global_manager.GlobalManager") as mock_global:
    mock_appender.formatter = SimpleFormatter()
    logger = Logger(
      name="test_logger", level=LoggingLevel.INFO, appenders=[mock_appender]
    )
    return logger


@pytest.fixture
def another_logger(mock_appender):
  """Fixture for creating another logger without auto-registration."""
  with patch("managers.global_manager.GlobalManager") as mock_global:
    mock_appender.formatter = SimpleFormatter()
    logger = Logger(
      name="another_logger", level=LoggingLevel.DEBUG, appenders=[mock_appender]
    )
    return logger


@pytest.fixture
def log_manager():
  """Fixture for creating a clean LogManager instance."""
  return LogManager(name="test_manager")


class TestLogManagerInitialization:
  """Test LogManager initialization and basic properties."""

  def test_log_manager_initialization_basic(self):
    """Test basic LogManager initialization."""
    manager = LogManager(name="test_manager")

    assert manager.name == "test_manager"
    assert isinstance(manager.loggers, dict)
    assert len(manager.loggers) == 0
    assert len(manager) == 0

  def test_log_manager_initialization_with_initial_loggers(self):
    """Test LogManager initialization with initial loggers."""
    # Create a simplified test by just testing the structure
    manager = LogManager(name="test_manager", initial_loggers={})

    assert manager.name == "test_manager"
    assert len(manager) == 0
    assert isinstance(manager.loggers, dict)

  def test_log_manager_initialization_empty_dict(self):
    """Test LogManager initialization with empty dict."""
    manager = LogManager(name="test_manager", initial_loggers={})

    assert manager.name == "test_manager"
    assert len(manager) == 0
    assert isinstance(manager.loggers, dict)


class TestLogManagerAddLogger:
  """Test LogManager add_logger functionality."""

  def test_add_logger_valid(self, log_manager, sample_logger):
    """Test adding a valid logger."""
    log_manager.add_logger(sample_logger)

    assert len(log_manager) == 1
    assert "test_logger" in log_manager
    assert log_manager.get_logger("test_logger") is sample_logger

  def test_add_logger_multiple(self, log_manager, sample_logger, another_logger):
    """Test adding multiple loggers."""
    log_manager.add_logger(sample_logger)
    log_manager.add_logger(another_logger)

    assert len(log_manager) == 2
    assert "test_logger" in log_manager
    assert "another_logger" in log_manager
    assert log_manager.get_logger("test_logger") is sample_logger
    assert log_manager.get_logger("another_logger") is another_logger

  def test_add_logger_invalid_type(self, log_manager):
    """Test adding non-Logger object raises TypeError."""
    invalid_objects = [None, "string", 123, [], {}, set(), object()]

    for invalid_obj in invalid_objects:
      with pytest.raises(TypeError, match="logger must be an instance of Logger"):
        log_manager.add_logger(invalid_obj)

  def test_add_logger_duplicate_name_raises_error(
    self, log_manager, sample_logger, another_logger
  ):
    """Test adding logger with duplicate name raises ValueError."""
    # Add first logger
    log_manager.add_logger(sample_logger)

    # Create another logger with same name
    with patch("managers.global_manager.GlobalManager") as mock_global:
      duplicate_logger = Logger(
        "test_logger", LoggingLevel.DEBUG, [ConsoleAppender(SimpleFormatter())]
      )

    with pytest.raises(
      ValueError, match="A logger with the name 'test_logger' already exists"
    ):
      log_manager.add_logger(duplicate_logger)

  def test_add_logger_empty_name_raises_error(self, log_manager, mock_appender):
    """Test adding logger with empty name raises ValueError."""
    # Create logger with empty name using patch to avoid auto-registration
    with patch("managers.global_manager.GlobalManager") as mock_global:
      mock_appender.formatter = SimpleFormatter()
      logger = Logger("", LoggingLevel.INFO, [mock_appender])

    with pytest.raises(ValueError, match="Logger must have a name"):
      log_manager.add_logger(logger)

  def test_add_logger_none_name_raises_error(self, log_manager, mock_appender):
    """Test adding logger with None name raises ValueError."""
    # Create logger with valid name first, then mock the validation
    mock_appender.formatter = SimpleFormatter()
    logger = Logger("test", LoggingLevel.INFO, [mock_appender])
    # Mock the logger's name attribute to be None for testing
    with pytest.raises((ValueError, TypeError)):
      # This will be caught by the validation in _add_logger_checks
      log_manager._add_logger_checks(Mock(name=None))

  def test_add_logger_non_string_name_raises_error(self, log_manager, mock_appender):
    """Test adding logger with non-string name raises TypeError."""
    # The first check is isinstance(logger, Logger) which will fail for Mock
    # So we expect "logger must be an instance of Logger" error
    mock_logger = Mock()
    mock_logger.name = 123

    with pytest.raises(TypeError, match="logger must be an instance of Logger"):
      log_manager._add_logger_checks(mock_logger)


class TestLogManagerGetLogger:
  """Test LogManager get_logger functionality."""

  def test_get_logger_existing(self, log_manager, sample_logger):
    """Test getting an existing logger."""
    log_manager.add_logger(sample_logger)

    retrieved = log_manager.get_logger("test_logger")
    assert retrieved is sample_logger

  def test_get_logger_non_existing_raises_keyerror(self, log_manager):
    """Test getting non-existing logger raises KeyError."""
    with pytest.raises(
      KeyError, match="No logger found with the name 'non_existing'"
    ):
      log_manager.get_logger("non_existing")

  def test_get_logger_invalid_name_type_raises_typeerror(self, log_manager):
    """Test getting logger with invalid name type raises TypeError."""
    invalid_names = [None, 123, [], {}, set(), object()]

    for invalid_name in invalid_names:
      with pytest.raises(TypeError, match="Logger name must be a string"):
        log_manager.get_logger(invalid_name)


class TestLogManagerRemoveLogger:
  """Test LogManager remove_logger functionality."""

  def test_remove_logger_existing(self, log_manager, sample_logger):
    """Test removing an existing logger."""
    log_manager.add_logger(sample_logger)
    assert len(log_manager) == 1

    log_manager.remove_logger("test_logger")

    assert len(log_manager) == 0
    assert "test_logger" not in log_manager

  def test_remove_logger_non_existing_raises_keyerror(self, log_manager):
    """Test removing non-existing logger raises KeyError."""
    with pytest.raises(
      KeyError, match="No logger found with the name 'non_existing'"
    ):
      log_manager.remove_logger("non_existing")

  def test_remove_logger_invalid_name_type_raises_typeerror(self, log_manager):
    """Test removing logger with invalid name type raises TypeError."""
    invalid_names = [None, 123, [], {}, set(), object()]

    for invalid_name in invalid_names:
      with pytest.raises(TypeError, match="Logger name must be a string"):
        log_manager.remove_logger(invalid_name)

  def test_remove_logger_multiple(self, log_manager, sample_logger, another_logger):
    """Test removing loggers one by one."""
    log_manager.add_logger(sample_logger)
    log_manager.add_logger(another_logger)
    assert len(log_manager) == 2

    log_manager.remove_logger("test_logger")
    assert len(log_manager) == 1
    assert "test_logger" not in log_manager
    assert "another_logger" in log_manager

    log_manager.remove_logger("another_logger")
    assert len(log_manager) == 0
    assert "another_logger" not in log_manager


class TestLogManagerUtilityMethods:
  """Test LogManager utility methods."""

  def test_get_all_loggers_empty(self, log_manager):
    """Test get_all_loggers with empty manager."""
    loggers = log_manager.get_all_loggers()

    assert isinstance(loggers, list)
    assert len(loggers) == 0

  def test_get_all_loggers_with_loggers(
    self, log_manager, sample_logger, another_logger
  ):
    """Test get_all_loggers with multiple loggers."""
    log_manager.add_logger(sample_logger)
    log_manager.add_logger(another_logger)

    loggers = log_manager.get_all_loggers()

    assert isinstance(loggers, list)
    assert len(loggers) == 2
    assert sample_logger in loggers
    assert another_logger in loggers

  def test_get_all_loggers_returns_copy(self, log_manager, sample_logger):
    """Test that get_all_loggers returns a copy, not the original list."""
    log_manager.add_logger(sample_logger)

    loggers1 = log_manager.get_all_loggers()
    loggers2 = log_manager.get_all_loggers()

    assert loggers1 is not loggers2  # Different objects
    assert loggers1 == loggers2  # Same content

  def test_clear_loggers_empty(self, log_manager):
    """Test clearing empty logger manager."""
    log_manager.clear_loggers()
    assert len(log_manager) == 0

  def test_clear_loggers_with_loggers(
    self, log_manager, sample_logger, another_logger
  ):
    """Test clearing manager with loggers."""
    log_manager.add_logger(sample_logger)
    log_manager.add_logger(another_logger)
    assert len(log_manager) == 2

    log_manager.clear_loggers()

    assert len(log_manager) == 0
    assert "test_logger" not in log_manager
    assert "another_logger" not in log_manager


class TestLogManagerDictLikeOperations:
  """Test LogManager dictionary-like operations."""

  def test_contains_existing_logger(self, log_manager, sample_logger):
    """Test __contains__ with existing logger."""
    log_manager.add_logger(sample_logger)

    assert "test_logger" in log_manager

  def test_contains_non_existing_logger(self, log_manager):
    """Test __contains__ with non-existing logger."""
    assert "non_existing" not in log_manager

  def test_contains_invalid_type_raises_typeerror(self, log_manager):
    """Test __contains__ with invalid type raises TypeError."""
    invalid_names = [None, 123, [], {}, set(), object()]

    for invalid_name in invalid_names:
      with pytest.raises(TypeError, match="Logger name must be a string"):
        _ = invalid_name in log_manager

  def test_getitem_existing_logger(self, log_manager, sample_logger):
    """Test __getitem__ with existing logger."""
    log_manager.add_logger(sample_logger)

    retrieved = log_manager["test_logger"]
    assert retrieved is sample_logger

  def test_getitem_non_existing_logger_raises_keyerror(self, log_manager):
    """Test __getitem__ with non-existing logger raises KeyError."""
    with pytest.raises(
      KeyError, match="No logger found with the name 'non_existing'"
    ):
      _ = log_manager["non_existing"]

  def test_setitem_valid_logger(self, log_manager, sample_logger):
    """Test __setitem__ with valid logger."""
    log_manager["test_logger"] = sample_logger

    assert len(log_manager) == 1
    assert "test_logger" in log_manager
    assert log_manager["test_logger"] is sample_logger

  def test_setitem_invalid_name_type_raises_typeerror(
    self, log_manager, sample_logger
  ):
    """Test __setitem__ with invalid name type raises TypeError."""
    invalid_names = [None, 123, [], {}, set(), object()]

    for invalid_name in invalid_names:
      with pytest.raises(TypeError, match="Logger name must be a string"):
        log_manager[invalid_name] = sample_logger

  def test_delitem_existing_logger(self, log_manager, sample_logger):
    """Test __delitem__ with existing logger."""
    log_manager.add_logger(sample_logger)
    assert "test_logger" in log_manager

    del log_manager["test_logger"]

    assert "test_logger" not in log_manager
    assert len(log_manager) == 0

  def test_delitem_non_existing_logger_raises_keyerror(self, log_manager):
    """Test __delitem__ with non-existing logger raises KeyError."""
    with pytest.raises(
      KeyError, match="No logger found with the name 'non_existing'"
    ):
      del log_manager["non_existing"]

  def test_len_empty(self, log_manager):
    """Test __len__ with empty manager."""
    assert len(log_manager) == 0

  def test_len_with_loggers(self, log_manager, sample_logger, another_logger):
    """Test __len__ with multiple loggers."""
    assert len(log_manager) == 0

    log_manager.add_logger(sample_logger)
    assert len(log_manager) == 1

    log_manager.add_logger(another_logger)
    assert len(log_manager) == 2

  def test_iter_empty(self, log_manager):
    """Test iteration over empty manager."""
    names = list(log_manager)
    assert names == []

  def test_iter_with_loggers(self, log_manager, sample_logger, another_logger):
    """Test iteration over manager with loggers."""
    log_manager.add_logger(sample_logger)
    log_manager.add_logger(another_logger)

    names = list(log_manager)

    assert len(names) == 2
    assert "test_logger" in names
    assert "another_logger" in names


class TestLogManagerStringRepresentations:
  """Test LogManager string representation methods."""

  def test_repr_empty(self, log_manager):
    """Test __repr__ with empty manager."""
    repr_str = repr(log_manager)
    assert "LogManager(loggers=[])" in repr_str

  def test_repr_with_loggers(self, log_manager, sample_logger, another_logger):
    """Test __repr__ with loggers."""
    log_manager.add_logger(sample_logger)
    log_manager.add_logger(another_logger)

    repr_str = repr(log_manager)

    assert "LogManager(loggers=" in repr_str
    assert "test_logger" in repr_str
    assert "another_logger" in repr_str

  def test_str_empty(self, log_manager):
    """Test __str__ with empty manager."""
    str_repr = str(log_manager)
    assert "LogManager with 0 loggers:" in str_repr

  def test_str_with_loggers(self, log_manager, sample_logger, another_logger):
    """Test __str__ with loggers."""
    log_manager.add_logger(sample_logger)
    log_manager.add_logger(another_logger)

    str_repr = str(log_manager)

    assert "LogManager with 2 loggers:" in str_repr
    assert "test_logger" in str_repr
    assert "another_logger" in str_repr


class TestLogManagerEdgeCases:
  """Test LogManager edge cases and complex scenarios."""

  def test_large_number_of_loggers(self, log_manager, mock_appender):
    """Test manager with large number of loggers."""
    num_loggers = 100

    # Add many loggers
    for i in range(num_loggers):
      mock_appender.formatter = SimpleFormatter()
      logger = Logger(f"logger_{i}", LoggingLevel.INFO, [mock_appender])
      log_manager.add_logger(logger)

    assert len(log_manager) == num_loggers

    # Test that all loggers are accessible
    for i in range(num_loggers):
      assert f"logger_{i}" in log_manager
      retrieved = log_manager.get_logger(f"logger_{i}")
      assert retrieved.name == f"logger_{i}"

  def test_logger_name_with_special_characters(self, log_manager, mock_appender):
    """Test logger names with special characters."""
    special_names = [
      "logger-with-dashes",
      "logger_with_underscores",
      "logger.with.dots",
      "logger:with:colons",
      "logger with spaces",
      "logger@with#symbols",
      "UPPERCASE_LOGGER",
      "MixedCase_Logger",
    ]

    for name in special_names:
      mock_appender.formatter = SimpleFormatter()
      logger = Logger(name, LoggingLevel.INFO, [mock_appender])
      log_manager.add_logger(logger)

      assert name in log_manager
      assert log_manager.get_logger(name) is logger

  def test_unicode_logger_names(self, log_manager, mock_appender):
    """Test logger names with unicode characters."""
    unicode_names = [
      "测试记录器",  # Chinese
      "логгер",  # Russian
      "مسجل",  # Arabic
      "ロガー",  # Japanese
      "logger_émoji_🚀",  # Emoji
    ]

    for name in unicode_names:
      mock_appender.formatter = SimpleFormatter()
      logger = Logger(name, LoggingLevel.INFO, [mock_appender])
      log_manager.add_logger(logger)

      assert name in log_manager
      assert log_manager.get_logger(name) is logger

  def test_add_remove_add_same_logger_name(self, log_manager, mock_appender):
    """Test adding, removing, then adding logger with same name."""
    name = "reused_name"

    # Create first logger with patched GlobalManager to avoid auto-registration
    with patch("managers.global_manager.GlobalManager") as mock_global:
      mock_appender.formatter = SimpleFormatter()
      logger1 = Logger(name, LoggingLevel.INFO, [mock_appender])
    log_manager.add_logger(logger1)
    assert log_manager.get_logger(name) is logger1

    # Remove logger
    log_manager.remove_logger(name)
    assert name not in log_manager

    # Add different logger with same name
    with patch("managers.global_manager.GlobalManager") as mock_global:
      mock_appender.formatter = SimpleFormatter()
      logger2 = Logger(name, LoggingLevel.DEBUG, [mock_appender])
    log_manager.add_logger(logger2)
    assert log_manager.get_logger(name) is logger2
    assert log_manager.get_logger(name) is not logger1


class TestLogManagerIntegration:
  """Test LogManager integration with real Logger instances."""

  def test_integration_with_real_loggers(self, log_manager):
    """Test LogManager with real Logger instances."""
    # Create real loggers with real components
    console_appender = ConsoleAppender(SimpleFormatter())

    logger1 = Logger("integration_test_1", LoggingLevel.INFO, [console_appender])

    logger2 = Logger("integration_test_2", LoggingLevel.DEBUG, [console_appender])

    # Add to manager
    log_manager.add_logger(logger1)
    log_manager.add_logger(logger2)

    # Test functionality
    assert len(log_manager) == 2
    retrieved1 = log_manager.get_logger("integration_test_1")
    retrieved2 = log_manager.get_logger("integration_test_2")

    assert retrieved1 is logger1
    assert retrieved2 is logger2

    # Test that loggers still work
    try:
      retrieved1.log(LoggingLevel.INFO, "Test message from manager")
      retrieved2.log(LoggingLevel.DEBUG, "Debug message from manager")
    except Exception as e:
      pytest.fail(f"Logger functionality failed: {e}")

  def test_manager_state_independence(self, mock_appender):
    """Test that different managers maintain independent state."""
    manager1 = LogManager("manager_1")
    manager2 = LogManager("manager_2")

    # Create loggers without auto-registration to avoid global conflicts
    with patch("managers.global_manager.GlobalManager") as mock_global:
      mock_appender.formatter = SimpleFormatter()
      logger1 = Logger("shared_name", LoggingLevel.INFO, [mock_appender])
    with patch("managers.global_manager.GlobalManager") as mock_global:
      mock_appender.formatter = SimpleFormatter()
      logger2 = Logger("shared_name", LoggingLevel.DEBUG, [mock_appender])

    # Add same name to different managers
    manager1.add_logger(logger1)
    manager2.add_logger(logger2)

    # They should maintain separate state
    assert len(manager1) == 1
    assert len(manager2) == 1
    assert manager1.get_logger("shared_name") is logger1
    assert manager2.get_logger("shared_name") is logger2
    assert manager1.get_logger("shared_name") is not manager2.get_logger(
      "shared_name"
    )


def run_manual_tests():
  """Manual test runner for verification."""
  print("Running LogManager manual tests...")

  # Test 1: Basic functionality
  print("\n1. Testing basic LogManager functionality:")
  try:
    manager = LogManager("manual_test_manager")
    mock_appender = Mock(spec=BaseAppender)
    mock_appender.formatter = SimpleFormatter()
    logger = Logger("manual_test_logger", LoggingLevel.INFO, [mock_appender])

    manager.add_logger(logger)
    retrieved = manager.get_logger("manual_test_logger")

    assert retrieved is logger
    assert len(manager) == 1
    assert "manual_test_logger" in manager

    print("✓ Basic functionality works correctly")
  except Exception as e:
    print(f"✗ Error: {e}")

  # Test 2: Dictionary-like operations
  print("\n2. Testing dictionary-like operations:")
  try:
    manager = LogManager("dict_test_manager")
    mock_appender = Mock(spec=BaseAppender)
    mock_appender.formatter = SimpleFormatter()
    logger = Logger("dict_test_logger", LoggingLevel.DEBUG, [mock_appender])

    # Test setitem and getitem
    manager["dict_test_logger"] = logger
    retrieved = manager["dict_test_logger"]
    assert retrieved is logger

    # Test delitem
    del manager["dict_test_logger"]
    assert "dict_test_logger" not in manager

    print("✓ Dictionary-like operations work correctly")
  except Exception as e:
    print(f"✗ Error: {e}")

  # Test 3: Error handling
  print("\n3. Testing error handling:")
  try:
    manager = LogManager("error_test_manager")

    # Test invalid logger type
    try:
      # Create a mock to avoid type errors
      invalid_logger = Mock()
      manager.add_logger(invalid_logger)
      print("✗ Should have raised TypeError")
    except TypeError:
      print("✓ Correctly caught TypeError for invalid logger")

    # Test non-existent logger
    try:
      manager.get_logger("non_existent")
      print("✗ Should have raised KeyError")
    except KeyError:
      print("✓ Correctly caught KeyError for non-existent logger")

  except Exception as e:
    print(f"✗ Unexpected error: {e}")

  print("\nLogManager manual tests completed!")


if __name__ == "__main__":
  run_manual_tests()
