#!/usr/bin/env python3
# mypy: ignore-errors
"""
Test suite for SQLiteAppender class.

This module tests the SQLiteAppender functionality including:
- Database connection and initialization
- Table creation
- Log record insertion
- Error handling and teardown
- Configuration from dictionary
- Filter integration

All database operations are mocked to avoid actual SQLite file creation.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appenders.sqlite_appender import SQLiteAppender
from core.record import LogRecord
from core.level import LoggingLevel
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter


@pytest.fixture
def mock_sqlite_connection():
    """Fixture for mocking SQLite connection and cursor."""
    with patch("sqlite3.connect") as mock_connect:
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        yield mock_connection, mock_cursor


@pytest.fixture
def sample_log_record():
    """Fixture for creating a sample log record."""
    record = LogRecord(level=LoggingLevel.INFO, message="Test log message")
    # Set a specific timestamp for testing
    record.set_timestamp(datetime(2025, 6, 29, 10, 30, 15))
    return record


class TestSQLiteAppenderInitialization:
    """Test SQLiteAppender initialization and setup."""

    def test_init_success(self, mock_sqlite_connection):
        """Test successful SQLiteAppender initialization."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db")

        assert appender.db_path == "test.db"
        assert appender.table_name == "logs"
        assert appender._connection is mock_connection
        assert appender._cursor is mock_cursor

        # Verify table creation was called
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()

    def test_init_custom_table_name(self, mock_sqlite_connection):
        """Test initialization with custom table name."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db", table_name="custom_logs")

        assert appender.table_name == "custom_logs"

    def test_init_with_filters(self, mock_sqlite_connection):
        """Test initialization with filters."""
        mock_connection, mock_cursor = mock_sqlite_connection
        filters = [KeywordFilter(["test"]), LevelFilter(LoggingLevel.ERROR)]

        appender = SQLiteAppender(db_path="test.db", filters=filters)

        assert len(appender.filters) == 2
        assert isinstance(appender.filters[0], KeywordFilter)
        assert isinstance(appender.filters[1], LevelFilter)

    def test_init_empty_filters(self, mock_sqlite_connection):
        """Test initialization with empty filters list."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db", filters=[])

        assert appender.filters == []


class TestSQLiteAppenderAppend:
    """Test SQLiteAppender log record appending."""

    def test_append_log_record(self, mock_sqlite_connection, sample_log_record):
        """Test appending a log record."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db")
        appender.append(sample_log_record)

        # Verify INSERT query was executed
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) >= 1

        # Verify commit was called
        assert (
            mock_connection.commit.call_count >= 2
        )  # Once for table creation, once for insert

    def test_append_with_filters_pass(self, mock_sqlite_connection, sample_log_record):
        """Test appending with filters that allow the record."""
        mock_connection, mock_cursor = mock_sqlite_connection

        # Create filter that should pass
        keyword_filter = KeywordFilter(["Test"])
        level_filter = LevelFilter(LoggingLevel.DEBUG)  # DEBUG and above

        appender = SQLiteAppender(
            db_path="test.db", filters=[keyword_filter, level_filter]
        )

        appender.append(sample_log_record)

        # Should have executed INSERT (plus table creation)
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) >= 1

    def test_append_with_filters_block(self, mock_sqlite_connection):
        """Test appending with filters that block the record."""
        mock_connection, mock_cursor = mock_sqlite_connection

        # Create filter that should block
        keyword_filter = KeywordFilter(["blocked"])

        appender = SQLiteAppender(db_path="test.db", filters=[keyword_filter])

        log_record = LogRecord(
            level=LoggingLevel.INFO, message="This message should be filtered"
        )

        appender.append(log_record)

        # Should only have table creation, no INSERT for the log
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) == 0

    def test_append_no_filters(self, mock_sqlite_connection, sample_log_record):
        """Test appending with no filters (should always append)."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db", filters=[])
        appender.append(sample_log_record)

        # Should have executed INSERT
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) >= 1


class TestSQLiteAppenderTeardown:
    """Test SQLiteAppender cleanup and teardown."""

    def test_teardown(self, mock_sqlite_connection):
        """Test proper teardown of connections."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db")
        appender.teardown()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_del_calls_teardown(self, mock_sqlite_connection):
        """Test that __del__ calls teardown."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db")

        # Manually call __del__ since Python's garbage collection timing is unpredictable
        appender.__del__()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


class TestSQLiteAppenderSerialization:
    """Test SQLiteAppender serialization methods."""

    @patch("sqlite3.connect")
    def test_from_dict_success(self, mock_connect):
        """Test creation from dictionary."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        data = {"db_path": "test.db", "table_name": "custom_logs"}

        appender = SQLiteAppender.from_dict(data)

        assert appender.db_path == "test.db"
        assert appender.table_name == "custom_logs"

    @patch("sqlite3.connect")
    def test_from_dict_with_filters(self, mock_connect):
        """Test creation from dictionary with filters."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mock the filter creation process
        with patch("appenders.sqlite_appender.StringToFilter") as mock_string_to_filter:
            mock_keyword_filter_class = Mock()
            mock_level_filter_class = Mock()

            # Set up mock filter instances
            mock_keyword_filter = Mock(spec=KeywordFilter)
            mock_level_filter = Mock(spec=LevelFilter)

            mock_keyword_filter_class.from_dict.return_value = mock_keyword_filter
            mock_level_filter_class.from_dict.return_value = mock_level_filter

            def mock_string_to_filter_func(filter_type):
                if filter_type == "keyword":
                    return mock_keyword_filter_class
                elif filter_type == "level":
                    return mock_level_filter_class
                else:
                    raise ValueError(f"Unknown filter type: {filter_type}")

            mock_string_to_filter.side_effect = mock_string_to_filter_func

            data = {
                "db_path": "test.db",
                "filters": [
                    {"type": "keyword", "keywords": ["test", "debug"]},
                    {"type": "level", "level": "ERROR"},
                ],
            }

            appender = SQLiteAppender.from_dict(data)

            assert appender.db_path == "test.db"
            assert appender.filters is not None
            assert len(appender.filters) == 2

    def test_from_dict_missing_db_path(self):
        """Test from_dict with missing db_path."""
        with pytest.raises(
            ValueError, match="db_path must be in the config dictionary"
        ):
            SQLiteAppender.from_dict({"table_name": "logs"})

    def test_from_dict_invalid_db_path_type(self):
        """Test from_dict with invalid db_path type."""
        with pytest.raises(ValueError, match="db_path must be a string"):
            SQLiteAppender.from_dict({"db_path": 123})


class TestSQLiteAppenderTableCreation:
    """Test SQLiteAppender table creation functionality."""

    def test_table_creation_query_format(self, mock_sqlite_connection):
        """Test that table creation query is properly formatted."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db", table_name="test_table")

        # Check that table creation was called
        create_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "CREATE TABLE" in str(call)
        ]
        assert len(create_calls) >= 1

        # Verify table name is in the query
        create_call_args = str(create_calls[0])
        assert "test_table" in create_call_args

    def test_default_table_structure(self, mock_sqlite_connection):
        """Test that the default table structure is created correctly."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db")

        # Verify table creation includes expected columns
        create_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "CREATE TABLE" in str(call)
        ]
        assert len(create_calls) >= 1

        create_query = str(create_calls[0])
        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in create_query
        assert "timestamp TEXT NOT NULL" in create_query
        assert "level TEXT NOT NULL" in create_query
        assert "message TEXT NOT NULL" in create_query


class TestSQLiteAppenderEdgeCases:
    """Test SQLiteAppender edge cases and error conditions."""

    def test_multiple_appends(self, mock_sqlite_connection):
        """Test multiple log record appends."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db")

        # Append multiple records
        for i in range(3):
            record = LogRecord(level=LoggingLevel.INFO, message=f"Test message {i}")
            appender.append(record)

        # Should have 3 INSERT calls (plus table creation)
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) == 3

    def test_different_log_levels(self, mock_sqlite_connection):
        """Test appending records with different log levels."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db")

        levels = [
            LoggingLevel.DEBUG,
            LoggingLevel.INFO,
            LoggingLevel.WARNING,
            LoggingLevel.ERROR,
            LoggingLevel.CRITICAL,
        ]

        for level in levels:
            record = LogRecord(level=level, message=f"Test {level} message")
            appender.append(record)

        # Should have 5 INSERT calls
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) == 5

    def test_none_filters_defaults_to_empty(self, mock_sqlite_connection):
        """Test that None filters defaults to empty list."""
        mock_connection, mock_cursor = mock_sqlite_connection

        appender = SQLiteAppender(db_path="test.db", filters=None)

        assert appender.filters == []


if __name__ == "__main__":
    pytest.main([__file__])
