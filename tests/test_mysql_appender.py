#!/usr/bin/env python3
# mypy: ignore-errors
"""
Test suite for MySQLAppender class.

This module tests the MySQLAppender functionality including:
- Connection management and initialization
- Database table creation
- Log record insertion
- Error handling and teardown
- Configuration from dictionary
- Filter integration

All database operations are mocked to avoid actual MySQL connections.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appenders.mysql_appender import MySQLAppender, MySQLConnectionException
from core.record import LogRecord
from core.level import LoggingLevel
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter


@pytest.fixture
def mock_mysql_connection():
    """Fixture for mocking MySQL connection and cursor."""
    with patch("appenders.mysql_appender.MySQLConnection") as mock_conn_class:
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn_class.return_value = mock_connection

        yield mock_connection, mock_cursor


@pytest.fixture
def sample_log_record():
    """Fixture for creating a sample log record."""
    record = LogRecord(level=LoggingLevel.INFO, message="Test log message")
    # Set a specific timestamp for testing
    record.set_timestamp(datetime(2025, 6, 29, 10, 30, 15))
    return record


class TestMySQLAppenderInitialization:
    """Test MySQLAppender initialization and setup."""

    def test_init_success(self, mock_mysql_connection):
        """Test successful MySQLAppender initialization."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost", user="testuser", password="testpass", database="testdb"
        )

        assert appender.host == "localhost"
        assert appender.user == "testuser"
        assert appender.password == "testpass"
        assert appender.database == "testdb"
        assert appender.table_name == "logs"
        assert appender._connection is mock_connection
        assert appender._cursor is mock_cursor

        # Verify table creation was called
        mock_cursor.execute.assert_called()
        # With autocommit=True (default), commit should not be called
        mock_connection.commit.assert_not_called()

    def test_init_custom_table_name(self, mock_mysql_connection):
        """Test initialization with custom table name."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb",
            table_name="custom_logs",
        )

        assert appender.table_name == "custom_logs"

    def test_init_with_filters(self, mock_mysql_connection):
        """Test initialization with filters."""
        mock_connection, mock_cursor = mock_mysql_connection
        filters = [KeywordFilter(["test"]), LevelFilter(LoggingLevel.ERROR)]

        appender = MySQLAppender(
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb",
            filters=filters,
        )

        assert len(appender.filters) == 2
        assert isinstance(appender.filters[0], KeywordFilter)
        assert isinstance(appender.filters[1], LevelFilter)

    @patch("appenders.mysql_appender.MySQLConnection")
    def test_init_connection_error(self, mock_conn_class):
        """Test initialization with connection error."""
        import mysql.connector

        mock_conn_class.side_effect = mysql.connector.Error("Connection failed")

        with pytest.raises(MySQLConnectionException, match="Error connecting to MySQL"):
            MySQLAppender(
                host="invalid", user="testuser", password="testpass", database="testdb"
            )


class TestMySQLAppenderAppend:
    """Test MySQLAppender log record appending."""

    def test_append_log_record(self, mock_mysql_connection, sample_log_record):
        """Test appending a log record."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost", user="testuser", password="testpass", database="testdb"
        )

        appender.append(sample_log_record)

        # Verify INSERT query was executed
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) >= 1

        # With autocommit=True (default), commit should not be called
        assert mock_connection.commit.call_count == 0

    def test_append_with_filters_pass(self, mock_mysql_connection, sample_log_record):
        """Test appending with filters that allow the record."""
        mock_connection, mock_cursor = mock_mysql_connection

        # Create filter that should pass
        keyword_filter = KeywordFilter(["Test"])
        level_filter = LevelFilter(LoggingLevel.DEBUG)  # DEBUG and above

        appender = MySQLAppender(
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb",
            filters=[keyword_filter, level_filter],
        )

        appender.append(sample_log_record)

        # Should have executed INSERT (plus table creation)
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) >= 1

    def test_append_with_filters_block(self, mock_mysql_connection):
        """Test appending with filters that block the record."""
        mock_connection, mock_cursor = mock_mysql_connection

        # Create filter that should block
        keyword_filter = KeywordFilter(["blocked"])

        appender = MySQLAppender(
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb",
            filters=[keyword_filter],
        )

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


class TestMySQLAppenderTeardown:
    """Test MySQLAppender cleanup and teardown."""

    def test_teardown(self, mock_mysql_connection):
        """Test proper teardown of connections."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost", user="testuser", password="testpass", database="testdb"
        )

        appender.teardown()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_del_calls_teardown(self, mock_mysql_connection):
        """Test that __del__ calls teardown."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost", user="testuser", password="testpass", database="testdb"
        )

        # Manually call __del__ since Python's garbage collection timing is unpredictable
        appender.__del__()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


class TestMySQLAppenderSerialization:
    """Test MySQLAppender serialization methods."""

    def test_to_dict(self, mock_mysql_connection):
        """Test conversion to dictionary."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost", user="testuser", password="testpass", database="testdb"
        )

        result = appender.to_dict()

        expected = {
            "host": "localhost",
            "user": "testuser",
            "password": "testpass",
            "database": "testdb",
            "table_name": "logs",
            "autocommit": True,
            "reconnect": True,
            "connect_timeout": 10,
        }

        assert result == expected

    @patch("appenders.mysql_appender.MySQLConnection")
    def test_from_dict_success(self, mock_conn_class):
        """Test creation from dictionary."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn_class.return_value = mock_connection

        data = {
            "host": "localhost",
            "user": "testuser",
            "password": "testpass",
            "database": "testdb",
            "table_name": "custom_logs",
        }

        appender = MySQLAppender.from_dict(data)

        assert appender.host == "localhost"
        assert appender.user == "testuser"
        assert appender.password == "testpass"
        assert appender.database == "testdb"
        assert appender.table_name == "custom_logs"

    def test_from_dict_missing_required_fields(self):
        """Test from_dict with missing required fields."""

        # Missing host
        with pytest.raises(ValueError, match="'host' must be specified"):
            MySQLAppender.from_dict(
                {"user": "test", "password": "test", "database": "test"}
            )

        # Missing user
        with pytest.raises(ValueError, match="'user' must be specified"):
            MySQLAppender.from_dict(
                {"host": "test", "password": "test", "database": "test"}
            )

        # Missing password
        with pytest.raises(ValueError, match="'password' must be specified"):
            MySQLAppender.from_dict(
                {"host": "test", "user": "test", "database": "test"}
            )

    def test_from_dict_invalid_field_types(self):
        """Test from_dict with invalid field types."""

        # Invalid host type
        with pytest.raises(ValueError, match="'host' must be a string"):
            MySQLAppender.from_dict(
                {"host": 123, "user": "test", "password": "test", "database": "test"}
            )

        # Invalid user type
        with pytest.raises(ValueError, match="'user' must be a string"):
            MySQLAppender.from_dict(
                {"host": "test", "user": 123, "password": "test", "database": "test"}
            )


class TestMySQLAppenderEdgeCases:
    """Test MySQLAppender edge cases and error conditions."""

    def test_table_creation_query_format(self, mock_mysql_connection):
        """Test that table creation query is properly formatted."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb",
            table_name="test_table",
        )

        # Check that table creation was called with correct table name
        create_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "CREATE TABLE" in str(call)
        ]
        assert len(create_calls) >= 1

        # Verify table name is in the query
        create_call_args = str(create_calls[0])
        assert "test_table" in create_call_args

    def test_empty_filters_list(self, mock_mysql_connection, sample_log_record):
        """Test behavior with empty filters list."""
        mock_connection, mock_cursor = mock_mysql_connection

        appender = MySQLAppender(
            host="localhost",
            user="testuser",
            password="testpass",
            database="testdb",
            filters=[],
        )

        appender.append(sample_log_record)

        # Should still append the record
        insert_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "INSERT INTO" in str(call)
        ]
        assert len(insert_calls) >= 1


if __name__ == "__main__":
    pytest.main([__file__])
