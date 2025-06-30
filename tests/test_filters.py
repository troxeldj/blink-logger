# mypy: ignore-errors
"""
Comprehensive test suite for Filter classes

This module tests the filter functionality including:
- BaseFilter abstract interface
- KeywordFilter for keyword-based filtering
- LevelFilter for level-based filtering
- Filter integration with appenders
- Error handling and validation
- Edge cases and performance
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch
from typing import List
from io import StringIO

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
from filters.base_filter import BaseFilter
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter
from core.record import LogRecord
from core.level import LoggingLevel
from appenders.console_appender import ConsoleAppender
from appenders.composite_appender import CompositeAppender
from formatters.simple_formatter import SimpleFormatter


@pytest.fixture
def sample_log_record():
  """Fixture for creating a sample log record"""
  return LogRecord(
    level=LoggingLevel.INFO,
    message="This is a test message with keyword authentication",
    metadata={"user_id": 123, "action": "login"},
  )


@pytest.fixture
def debug_log_record():
  """Fixture for creating a debug log record"""
  return LogRecord(
    level=LoggingLevel.DEBUG,
    message="Debug information for troubleshooting",
    metadata={"debug_level": 1},
  )


@pytest.fixture
def error_log_record():
  """Fixture for creating an error log record"""
  return LogRecord(
    level=LoggingLevel.ERROR,
    message="Critical error occurred in database connection",
    metadata={"error_code": 500, "component": "database"},
  )


class TestBaseFilter:
  """Test the BaseFilter abstract class"""

  def test_base_filter_is_abstract(self):
    """Test that BaseFilter cannot be instantiated directly"""
    with pytest.raises(TypeError):
      BaseFilter()  # type: ignore

  def test_base_filter_subclass_must_implement_should_log(self):
    """Test that subclasses must implement should_log method"""

    class IncompleteFilter(BaseFilter):
      pass

    with pytest.raises(TypeError):
      IncompleteFilter()  # type: ignore

  def test_base_filter_subclass_with_implementation(self):
    """Test that subclasses can be instantiated when should_log is implemented"""

    class ValidFilter(BaseFilter):
      def should_log(self, record: LogRecord) -> bool:
        return True

      @classmethod
      def from_dict(cls, data: dict) -> "ValidFilter":
        return cls()

      def to_dict(self) -> dict:
        return {"type": "ValidFilter"}

    filter_instance = ValidFilter()
    assert isinstance(filter_instance, BaseFilter)


class TestKeywordFilter:
  """Test the KeywordFilter class"""

  def test_keyword_filter_initialization_empty(self):
    """Test KeywordFilter initialization with no keywords"""
    filter_obj = KeywordFilter()
    assert filter_obj.keywords == []

  def test_keyword_filter_initialization_none(self):
    """Test KeywordFilter initialization with None keywords"""
    filter_obj = KeywordFilter(keywords=None)
    assert filter_obj.keywords == []

  def test_keyword_filter_initialization_single_string(self):
    """Test KeywordFilter initialization with single string keyword"""
    filter_obj = KeywordFilter(keywords="authentication")
    assert filter_obj.keywords == ["authentication"]

  def test_keyword_filter_initialization_list_of_strings(self):
    """Test KeywordFilter initialization with list of keywords"""
    keywords = ["error", "warning", "critical"]
    filter_obj = KeywordFilter(keywords=keywords)
    assert filter_obj.keywords == keywords

  def test_keyword_filter_initialization_invalid_type(self):
    """Test KeywordFilter initialization with invalid keyword type"""
    with pytest.raises(
      ValueError, match="Keywords must be a string or a list of strings"
    ):
      KeywordFilter(keywords=123)  # type: ignore

  def test_keyword_filter_initialization_mixed_types_in_list(self):
    """Test KeywordFilter initialization with mixed types in list"""
    with pytest.raises(ValueError, match="All keywords must be strings"):
      KeywordFilter(keywords=["valid", 123, "also_valid"])  # type: ignore

  def test_keyword_filter_should_log_match_found(self, sample_log_record):
    """Test should_log returns True when keyword is found"""
    filter_obj = KeywordFilter(keywords=["authentication", "login"])
    assert filter_obj.should_log(sample_log_record) is True

  def test_keyword_filter_should_log_no_match(self, sample_log_record):
    """Test should_log returns False when no keyword is found"""
    filter_obj = KeywordFilter(keywords=["database", "connection"])
    assert filter_obj.should_log(sample_log_record) is False

  def test_keyword_filter_should_log_empty_keywords(self, sample_log_record):
    """Test should_log with empty keywords list"""
    filter_obj = KeywordFilter(keywords=[])
    assert filter_obj.should_log(sample_log_record) is False

  def test_keyword_filter_should_log_partial_match(self, sample_log_record):
    """Test should_log with partial keyword matches"""
    filter_obj = KeywordFilter(keywords=["test"])
    assert filter_obj.should_log(sample_log_record) is True

  def test_keyword_filter_should_log_case_sensitive(self):
    """Test should_log is case sensitive"""
    record = LogRecord(level=LoggingLevel.INFO, message="This is a TEST message")
    filter_obj = KeywordFilter(keywords=["test"])
    assert filter_obj.should_log(record) is False

    filter_obj_upper = KeywordFilter(keywords=["TEST"])
    assert filter_obj_upper.should_log(record) is True

  def test_keyword_filter_should_log_multiple_keywords(self):
    """Test should_log with multiple keywords where any match succeeds"""
    record = LogRecord(
      level=LoggingLevel.INFO, message="database connection failed"
    )
    filter_obj = KeywordFilter(keywords=["authentication", "database", "session"])
    assert filter_obj.should_log(record) is True


class TestLevelFilter:
  """Test the LevelFilter class"""

  def test_level_filter_initialization_valid(self):
    """Test LevelFilter initialization with valid level"""
    filter_obj = LevelFilter(level=LoggingLevel.WARNING)
    assert filter_obj.level == LoggingLevel.WARNING

  def test_level_filter_initialization_invalid_none(self):
    """Test LevelFilter initialization with None level"""
    with pytest.raises(ValueError, match="Invalid logging level provided"):
      LevelFilter(level=None)  # type: ignore

  def test_level_filter_initialization_invalid_type(self):
    """Test LevelFilter initialization with invalid type"""
    with pytest.raises(ValueError, match="Invalid logging level provided"):
      LevelFilter(level="INFO")  # type: ignore

  def test_level_filter_should_log_equal_level(self, sample_log_record):
    """Test should_log returns True when levels are equal"""
    filter_obj = LevelFilter(level=LoggingLevel.INFO)
    assert filter_obj.should_log(sample_log_record) is True

  def test_level_filter_should_log_higher_level(self, error_log_record):
    """Test should_log returns True when record level is higher"""
    filter_obj = LevelFilter(level=LoggingLevel.WARNING)
    assert filter_obj.should_log(error_log_record) is True

  def test_level_filter_should_log_lower_level(self, debug_log_record):
    """Test should_log returns False when record level is lower"""
    filter_obj = LevelFilter(level=LoggingLevel.INFO)
    assert filter_obj.should_log(debug_log_record) is False

  def test_level_filter_should_log_all_levels(self):
    """Test should_log behavior across all logging levels"""
    filter_obj = LevelFilter(level=LoggingLevel.WARNING)

    # Records with levels below WARNING should be filtered out
    debug_record = LogRecord(LoggingLevel.DEBUG, "Debug")
    info_record = LogRecord(LoggingLevel.INFO, "Info")
    assert filter_obj.should_log(debug_record) is False
    assert filter_obj.should_log(info_record) is False

    # Records with levels at or above WARNING should pass
    warning_record = LogRecord(LoggingLevel.WARNING, "Warning")
    error_record = LogRecord(LoggingLevel.ERROR, "Error")
    critical_record = LogRecord(LoggingLevel.CRITICAL, "Critical")
    assert filter_obj.should_log(warning_record) is True
    assert filter_obj.should_log(error_record) is True
    assert filter_obj.should_log(critical_record) is True

  def test_level_filter_debug_level_allows_all(self):
    """Test that DEBUG level filter allows all log levels"""
    filter_obj = LevelFilter(level=LoggingLevel.DEBUG)

    for level in [
      LoggingLevel.DEBUG,
      LoggingLevel.INFO,
      LoggingLevel.WARNING,
      LoggingLevel.ERROR,
      LoggingLevel.CRITICAL,
    ]:
      record = LogRecord(level, "Test message")
      assert filter_obj.should_log(record) is True

  def test_level_filter_critical_level_most_restrictive(self):
    """Test that CRITICAL level filter only allows critical messages"""
    filter_obj = LevelFilter(level=LoggingLevel.CRITICAL)

    # Only CRITICAL should pass
    critical_record = LogRecord(LoggingLevel.CRITICAL, "Critical")
    assert filter_obj.should_log(critical_record) is True

    # All others should be filtered out
    for level in [
      LoggingLevel.DEBUG,
      LoggingLevel.INFO,
      LoggingLevel.WARNING,
      LoggingLevel.ERROR,
    ]:
      record = LogRecord(level, "Test message")
      assert filter_obj.should_log(record) is False


class TestFilterIntegration:
  """Test filter integration with appenders"""

  def test_console_appender_with_keyword_filter(self):
    """Test ConsoleAppender with KeywordFilter integration"""
    keyword_filter = KeywordFilter(keywords=["error", "critical"])
    appender = ConsoleAppender(
      formatter=SimpleFormatter(), filters=[keyword_filter]
    )

    # Verify the filter is properly stored
    assert len(appender.filters) == 1
    assert isinstance(appender.filters[0], KeywordFilter)

  def test_console_appender_with_level_filter(self):
    """Test ConsoleAppender with LevelFilter integration"""
    level_filter = LevelFilter(level=LoggingLevel.WARNING)
    appender = ConsoleAppender(formatter=SimpleFormatter(), filters=[level_filter])

    # Verify the filter is properly stored
    assert len(appender.filters) == 1
    assert isinstance(appender.filters[0], LevelFilter)

  def test_console_appender_with_multiple_filters(self):
    """Test ConsoleAppender with multiple filters"""
    keyword_filter = KeywordFilter(keywords=["error"])
    level_filter = LevelFilter(level=LoggingLevel.WARNING)
    appender = ConsoleAppender(
      formatter=SimpleFormatter(), filters=[keyword_filter, level_filter]
    )

    assert len(appender.filters) == 2
    assert isinstance(appender.filters[0], KeywordFilter)
    assert isinstance(appender.filters[1], LevelFilter)

  @patch("appenders.console_appender.sys.stdout", new_callable=StringIO)
  def test_filter_blocks_console_output(self, mock_stdout):
    """Test that filters block output when conditions aren't met"""
    keyword_filter = KeywordFilter(keywords=["database"])
    appender = ConsoleAppender(
      formatter=SimpleFormatter(), filters=[keyword_filter]
    )

    # This record should be blocked (no "database" keyword)
    record = LogRecord(LoggingLevel.INFO, "User authentication successful")
    appender.append(record)

    # No output should be written
    assert mock_stdout.getvalue() == ""

  @patch("appenders.console_appender.sys.stdout", new_callable=StringIO)
  def test_filter_allows_console_output(self, mock_stdout):
    """Test that filters allow output when conditions are met"""
    keyword_filter = KeywordFilter(keywords=["authentication"])
    appender = ConsoleAppender(
      formatter=SimpleFormatter(), filters=[keyword_filter]
    )

    # This record should pass (contains "authentication" keyword)
    record = LogRecord(LoggingLevel.INFO, "User authentication successful")
    appender.append(record)

    # Output should be written
    output = mock_stdout.getvalue()
    assert "authentication successful" in output

  def test_composite_appender_with_filters(self):
    """Test CompositeAppender with filters on individual appenders"""
    # Create appenders with different filters
    keyword_filter = KeywordFilter(keywords=["error"])
    level_filter = LevelFilter(level=LoggingLevel.WARNING)

    appender1 = ConsoleAppender(
      formatter=SimpleFormatter(), filters=[keyword_filter]
    )
    appender2 = ConsoleAppender(formatter=SimpleFormatter(), filters=[level_filter])

    composite = CompositeAppender(appenders=[appender1, appender2])

    # Verify filters are preserved in individual appenders
    assert len(composite.appenders[0].filters) == 1
    assert len(composite.appenders[1].filters) == 1

  def test_multiple_filters_all_must_pass(self):
    """Test that all filters must pass for a record to be logged"""
    # Create filters that would individually pass
    keyword_filter = KeywordFilter(keywords=["error"])
    level_filter = LevelFilter(level=LoggingLevel.INFO)

    appender = ConsoleAppender(
      formatter=SimpleFormatter(), filters=[keyword_filter, level_filter]
    )

    # Record that passes level filter but not keyword filter
    record1 = LogRecord(LoggingLevel.ERROR, "System failure occurred")
    # Record that passes keyword filter but not level filter
    record2 = LogRecord(LoggingLevel.DEBUG, "Debug error information")
    # Record that passes both filters
    record3 = LogRecord(LoggingLevel.ERROR, "Critical error detected")

    with patch(
      "appenders.console_appender.sys.stdout", new_callable=StringIO
    ) as mock_stdout:
      appender.append(record1)  # Should be blocked (no "error" keyword)
      appender.append(record2)  # Should be blocked (DEBUG < INFO)
      appender.append(record3)  # Should pass both filters

      output = mock_stdout.getvalue()
      # Only the third record should have been logged
      assert "Critical error detected" in output
      assert "System failure" not in output
      assert "Debug error" not in output


class TestFilterEdgeCases:
  """Test edge cases and error conditions for filters"""

  def test_keyword_filter_empty_message(self):
    """Test KeywordFilter with empty message"""
    filter_obj = KeywordFilter(keywords=["test"])
    record = LogRecord(LoggingLevel.INFO, "")
    assert filter_obj.should_log(record) is False

  def test_keyword_filter_unicode_keywords(self):
    """Test KeywordFilter with Unicode keywords"""
    filter_obj = KeywordFilter(keywords=["тест", "测试", "🔍"])

    record1 = LogRecord(LoggingLevel.INFO, "This is a тест message")
    record2 = LogRecord(LoggingLevel.INFO, "This contains 测试 characters")
    record3 = LogRecord(LoggingLevel.INFO, "Search 🔍 with emoji")
    record4 = LogRecord(LoggingLevel.INFO, "No matching characters")

    assert filter_obj.should_log(record1) is True
    assert filter_obj.should_log(record2) is True
    assert filter_obj.should_log(record3) is True
    assert filter_obj.should_log(record4) is False

  def test_level_filter_with_minimal_record(self):
    """Test LevelFilter with minimal LogRecord"""
    filter_obj = LevelFilter(level=LoggingLevel.INFO)
    record = LogRecord(LoggingLevel.WARNING, "Test")
    assert filter_obj.should_log(record) is True

  def test_appender_with_no_filters(self):
    """Test appender behavior with no filters"""
    appender = ConsoleAppender(formatter=SimpleFormatter())

    # Should have no filters
    assert appender.filters is None or len(appender.filters) == 0

    # Should log everything
    with patch(
      "appenders.console_appender.sys.stdout", new_callable=StringIO
    ) as mock_stdout:
      record = LogRecord(LoggingLevel.DEBUG, "Any message")
      appender.append(record)
      assert "Any message" in mock_stdout.getvalue()

  def test_appender_with_empty_filters_list(self):
    """Test appender behavior with empty filters list"""
    appender = ConsoleAppender(formatter=SimpleFormatter(), filters=[])

    # Should have empty filters list
    assert len(appender.filters) == 0

    # Should log everything (no filters to block)
    with patch(
      "appenders.console_appender.sys.stdout", new_callable=StringIO
    ) as mock_stdout:
      record = LogRecord(LoggingLevel.DEBUG, "Any message")
      appender.append(record)
      assert "Any message" in mock_stdout.getvalue()


class TestFilterPerformance:
  """Test filter performance and scalability"""

  def test_keyword_filter_large_keyword_list(self):
    """Test KeywordFilter performance with large keyword list"""
    large_keyword_list = [f"keyword_{i}" for i in range(1000)]
    filter_obj = KeywordFilter(keywords=large_keyword_list)

    # Test with matching keyword
    record1 = LogRecord(
      LoggingLevel.INFO, "This contains keyword_500 in the message"
    )
    assert filter_obj.should_log(record1) is True

    # Test with non-matching keyword
    record2 = LogRecord(LoggingLevel.INFO, "This contains no matching keywords")
    assert filter_obj.should_log(record2) is False

  def test_multiple_filters_performance(self):
    """Test performance with multiple filters"""
    filters = [
      KeywordFilter(keywords=[f"key_{i}" for i in range(10)]),
      LevelFilter(level=LoggingLevel.INFO),
      KeywordFilter(keywords=["test", "performance"]),
    ]

    appender = ConsoleAppender(formatter=SimpleFormatter(), filters=filters)

    # Test record that should pass all filters
    record = LogRecord(LoggingLevel.ERROR, "This is a key_5 test message")

    with patch(
      "appenders.console_appender.sys.stdout", new_callable=StringIO
    ) as mock_stdout:
      appender.append(record)
      # Should pass all filters and be logged
      assert "key_5 test message" in mock_stdout.getvalue()


if __name__ == "__main__":
  # If run directly, execute tests manually
  print("Running Filter tests manually...")

  failed = 0

  try:
    print("Testing BaseFilter abstract functionality...")

    # Test that BaseFilter cannot be instantiated
    try:
      BaseFilter()  # type: ignore
      print("❌ BaseFilter should not be instantiable")
      failed += 1
    except TypeError:
      print("✓ BaseFilter is properly abstract")

    # Test KeywordFilter
    print("Testing KeywordFilter...")
    keyword_filter = KeywordFilter(keywords=["test", "error"])
    record = LogRecord(LoggingLevel.INFO, "This is a test message")

    assert keyword_filter.should_log(record) is True
    print("✓ KeywordFilter matches keywords correctly")

    # Test LevelFilter
    print("Testing LevelFilter...")
    level_filter = LevelFilter(level=LoggingLevel.WARNING)
    debug_record = LogRecord(LoggingLevel.DEBUG, "Debug message")
    error_record = LogRecord(LoggingLevel.ERROR, "Error message")

    assert level_filter.should_log(debug_record) is False
    assert level_filter.should_log(error_record) is True
    print("✓ LevelFilter filters by level correctly")

    # Test integration with appenders
    print("Testing filter integration with appenders...")
    appender = ConsoleAppender(
      formatter=SimpleFormatter(), filters=[keyword_filter, level_filter]
    )

    assert len(appender.filters) == 2
    print("✓ Appender accepts multiple filters")

    print("✓ All manual filter tests passed!")

  except Exception as e:
    print(f"❌ Filter test failed: {e}")
    import traceback

    traceback.print_exc()
    failed += 1

  if failed == 0:
    print(f"\nAll manual tests passed! 🎉")
  else:
    print(f"\n{failed} tests failed. ❌")

  print("\nTo run with pytest: python -m pytest tests/test_filters.py -v")
