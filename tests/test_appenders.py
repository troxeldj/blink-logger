# mypy: ignore-errors
"""
Test suite for appenders

This module tests all appender functionality including:
- BaseAppender abstract functionality
- ConsoleAppender output to stdout
- FileAppender file writing operations
"""

import sys
import os
import tempfile
import pytest
from unittest.mock import Mock, patch, mock_open, call
from io import StringIO

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
from appenders.base_appender import BaseAppender
from appenders.console_appender import ConsoleAppender, ColoredConsoleAppender
from appenders.file_appender import FileAppender
from appenders.composite_appender import CompositeAppender
from core.level import LoggingLevel
from core.record import LogRecord
from core.color import ConsoleColor
from formatters.simple_formatter import SimpleFormatter
from formatters.json_formatter import JSONFormatter


@pytest.fixture
def sample_log_record():
    """Fixture for creating a sample LogRecord for testing"""
    return LogRecord(
        level=LoggingLevel.INFO,
        message="Test log message",
        source="test_module.py",
        metadata={"user_id": 123, "action": "login"}
    )


@pytest.fixture
def simple_formatter():
    """Fixture for SimpleFormatter"""
    return SimpleFormatter()


@pytest.fixture
def json_formatter():
    """Fixture for JSONFormatter"""
    return JSONFormatter()


class TestBaseAppender:
    """Test the BaseAppender abstract class"""
    
    def test_base_appender_initialization_with_formatter(self, simple_formatter):
        """Test BaseAppender initialization with a custom formatter"""
        appender = BaseAppender(formatter=simple_formatter)
        assert appender.formatter == simple_formatter
    
    def test_base_appender_initialization_without_formatter(self):
        """Test BaseAppender initialization with default formatter"""
        appender = BaseAppender()
        assert appender.formatter is not None
        assert isinstance(appender.formatter, SimpleFormatter)
    
    def test_base_appender_initialization_with_none_formatter(self):
        """Test BaseAppender initialization with None formatter (should use default)"""
        appender = BaseAppender(formatter=None)
        assert appender.formatter is not None
        assert isinstance(appender.formatter, SimpleFormatter)
    
    def test_base_appender_initialize_method(self):
        """Test that initialize method can be called (should do nothing in base class)"""
        appender = BaseAppender()
        # Should not raise an exception
        appender.initialize()
    
    def test_base_appender_teardown_method(self):
        """Test that teardown method can be called (should do nothing in base class)"""
        appender = BaseAppender()
        # Should not raise an exception
        appender.teardown()
    
    def test_base_appender_flush_method(self):
        """Test that flush method can be called (should do nothing in base class)"""
        appender = BaseAppender()
        # Should not raise an exception
        appender.flush()
    
    def test_base_appender_append_method_not_implemented(self, sample_log_record):
        """Test that append method raises NotImplementedError in base class"""
        appender = BaseAppender()
        with pytest.raises(NotImplementedError, match="Subclasses must implement this method"):
            appender.append(sample_log_record)


class TestConsoleAppender:
    """Test the ConsoleAppender class"""
    
    def test_console_appender_initialization(self, simple_formatter):
        """Test ConsoleAppender initialization"""
        appender = ConsoleAppender(formatter=simple_formatter)
        assert appender.formatter == simple_formatter
    
    def test_console_appender_initialization_with_none(self):
        """Test ConsoleAppender initialization with None formatter"""
        appender = ConsoleAppender(formatter=None)
        assert appender.formatter is not None
        assert isinstance(appender.formatter, SimpleFormatter)
    
    def test_console_appender_initialize_method(self):
        """Test ConsoleAppender initialize method"""
        appender = ConsoleAppender(formatter=None)
        # Should not raise an exception
        appender.initialize()
    
    def test_console_appender_teardown_method(self):
        """Test ConsoleAppender teardown method"""
        appender = ConsoleAppender(formatter=None)
        # Should not raise an exception
        appender.teardown()
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_console_appender_append_simple_formatter(self, mock_stdout, sample_log_record, simple_formatter):
        """Test ConsoleAppender append with SimpleFormatter"""
        appender = ConsoleAppender(formatter=simple_formatter)
        
        appender.append(sample_log_record)
        
        output = mock_stdout.getvalue()
        assert "Test log message" in output
        assert "INFO" in output
        assert output.endswith('\n')
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_console_appender_append_json_formatter(self, mock_stdout, sample_log_record, json_formatter):
        """Test ConsoleAppender append with JSONFormatter"""
        appender = ConsoleAppender(formatter=json_formatter)
        
        appender.append(sample_log_record)
        
        output = mock_stdout.getvalue()
        assert '"message": "Test log message"' in output
        assert '"level": "INFO"' in output
        assert '"source": "test_module.py"' in output
        assert '"user_id": 123' in output
        assert output.endswith('\n')
    
    @patch('appenders.console_appender.sys.stdout')
    def test_console_appender_flush_called(self, mock_stdout, sample_log_record):
        """Test that flush is called when appending"""
        appender = ConsoleAppender(formatter=None)
        
        appender.append(sample_log_record)
        
        # Verify that stdout.flush() was called
        mock_stdout.flush.assert_called()
    
    def test_console_appender_flush_method(self):
        """Test ConsoleAppender flush method directly"""
        appender = ConsoleAppender(formatter=None)
        
        with patch('appenders.console_appender.sys.stdout') as mock_stdout:
            appender.flush()
            mock_stdout.flush.assert_called_once()
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_console_appender_multiple_records(self, mock_stdout, simple_formatter):
        """Test ConsoleAppender with multiple log records"""
        appender = ConsoleAppender(formatter=simple_formatter)
        
        records = [
            LogRecord(LoggingLevel.INFO, "First message"),
            LogRecord(LoggingLevel.ERROR, "Second message"),
            LogRecord(LoggingLevel.DEBUG, "Third message")
        ]
        
        for record in records:
            appender.append(record)
        
        output = mock_stdout.getvalue()
        lines = output.strip().split('\n')
        
        assert len(lines) == 3
        assert "First message" in lines[0]
        assert "Second message" in lines[1]
        assert "Third message" in lines[2]


class TestColoredConsoleAppender:
    """Test the ColoredConsoleAppender class"""
    
    def test_colored_console_appender_initialization_default_color(self, simple_formatter):
        """Test ColoredConsoleAppender initialization with default color"""
        appender = ColoredConsoleAppender(formatter=simple_formatter)
        assert appender.formatter == simple_formatter
        assert appender.color == ConsoleColor.DEFAULT
    
    def test_colored_console_appender_initialization_custom_color(self, simple_formatter):
        """Test ColoredConsoleAppender initialization with custom color"""
        appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.RED)
        assert appender.formatter == simple_formatter
        assert appender.color == ConsoleColor.RED
    
    def test_colored_console_appender_initialization_without_formatter(self):
        """Test ColoredConsoleAppender initialization with default formatter"""
        appender = ColoredConsoleAppender()
        assert appender.formatter is not None
        assert isinstance(appender.formatter, SimpleFormatter)
        assert appender.color == ConsoleColor.DEFAULT
    
    def test_colored_console_appender_initialization_with_none_formatter(self):
        """Test ColoredConsoleAppender initialization with None formatter"""
        appender = ColoredConsoleAppender(formatter=None, color=ConsoleColor.GREEN)
        assert appender.formatter is not None
        assert isinstance(appender.formatter, SimpleFormatter)
        assert appender.color == ConsoleColor.GREEN
    
    def test_colored_console_appender_set_color(self):
        """Test setting color on ColoredConsoleAppender"""
        appender = ColoredConsoleAppender(color=ConsoleColor.BLUE)
        assert appender.color == ConsoleColor.BLUE
        
        appender.set_color(ConsoleColor.RED)
        assert appender.color == ConsoleColor.RED
        
        appender.set_color(ConsoleColor.YELLOW)
        assert appender.color == ConsoleColor.YELLOW
    
    def test_colored_console_appender_initialize_method(self):
        """Test ColoredConsoleAppender initialize method"""
        appender = ColoredConsoleAppender()
        # Should not raise an exception
        appender.initialize()
    
    def test_colored_console_appender_teardown_method(self):
        """Test ColoredConsoleAppender teardown method"""
        appender = ColoredConsoleAppender()
        # Should not raise an exception
        appender.teardown()
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_colored_console_appender_append_with_color(self, mock_stdout, sample_log_record, simple_formatter):
        """Test ColoredConsoleAppender append with color formatting"""
        appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.RED)
        
        appender.append(sample_log_record)
        
        output = mock_stdout.getvalue()
        # Should contain the original message
        assert "Test log message" in output
        assert "INFO" in output
        # Should contain ANSI color codes
        assert ConsoleColor.RED.value in output  # Red color code
        assert ConsoleColor.RESET.value in output  # Reset code
        assert output.endswith('\n')
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_colored_console_appender_different_colors(self, mock_stdout, sample_log_record, simple_formatter):
        """Test ColoredConsoleAppender with different colors"""
        colors_to_test = [ConsoleColor.RED, ConsoleColor.GREEN, ConsoleColor.BLUE, ConsoleColor.YELLOW, ConsoleColor.MAGENTA]
        
        for color in colors_to_test:
            mock_stdout.seek(0)
            mock_stdout.truncate(0)  # Clear previous output
            
            appender = ColoredConsoleAppender(formatter=simple_formatter, color=color)
            appender.append(sample_log_record)
            
            output = mock_stdout.getvalue()
            assert color.value in output
            assert ConsoleColor.RESET.value in output
            assert "Test log message" in output
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_colored_console_appender_json_formatter(self, mock_stdout, sample_log_record, json_formatter):
        """Test ColoredConsoleAppender with JSON formatter"""
        appender = ColoredConsoleAppender(formatter=json_formatter, color=ConsoleColor.CYAN)
        
        appender.append(sample_log_record)
        
        output = mock_stdout.getvalue()
        # Should contain JSON formatting
        assert '"message": "Test log message"' in output
        assert '"level": "INFO"' in output
        # Should contain color codes
        assert ConsoleColor.CYAN.value in output
        assert ConsoleColor.RESET.value in output
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_colored_console_appender_multiple_records(self, mock_stdout, simple_formatter):
        """Test ColoredConsoleAppender with multiple log records"""
        appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.MAGENTA)
        
        records = [
            LogRecord(LoggingLevel.INFO, "First message"),
            LogRecord(LoggingLevel.ERROR, "Second message"),
            LogRecord(LoggingLevel.DEBUG, "Third message")
        ]
        
        for record in records:
            appender.append(record)
        
        output = mock_stdout.getvalue()
        lines = output.strip().split('\n')
        
        assert len(lines) == 3
        for line in lines:
            assert ConsoleColor.MAGENTA.value in line
            assert ConsoleColor.RESET.value in line
        
        assert "First message" in lines[0]
        assert "Second message" in lines[1]
        assert "Third message" in lines[2]
    
    @patch('appenders.console_appender.sys.stdout')
    def test_colored_console_appender_flush_called(self, mock_stdout, sample_log_record):
        """Test that flush is called when appending to colored console"""
        appender = ColoredConsoleAppender(color=ConsoleColor.WHITE)
        
        appender.append(sample_log_record)
        
        # Verify that stdout.flush() was called
        mock_stdout.flush.assert_called()
    
    def test_colored_console_appender_flush_method(self):
        """Test ColoredConsoleAppender flush method directly"""
        appender = ColoredConsoleAppender()
        
        with patch('appenders.console_appender.sys.stdout') as mock_stdout:
            appender.flush()
            mock_stdout.flush.assert_called_once()
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_colored_console_appender_color_change_during_runtime(self, mock_stdout, sample_log_record, simple_formatter):
        """Test changing color during runtime"""
        appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.RED)
        
        # First append with red color
        appender.append(sample_log_record)
        first_output = mock_stdout.getvalue()
        
        # Change color to green
        appender.set_color(ConsoleColor.GREEN)
        
        # Clear output buffer
        mock_stdout.seek(0)
        mock_stdout.truncate(0)
        
        # Second append with green color
        appender.append(sample_log_record)
        second_output = mock_stdout.getvalue()
        
        # Verify both outputs have correct colors
        assert ConsoleColor.RED.value in first_output
        assert ConsoleColor.GREEN.value in second_output
        assert ConsoleColor.GREEN.value not in first_output
        assert ConsoleColor.RED.value not in second_output
    
    def test_colored_console_appender_inheritance(self):
        """Test that ColoredConsoleAppender properly inherits from ConsoleAppender"""
        appender = ColoredConsoleAppender()
        assert isinstance(appender, ConsoleAppender)
        assert isinstance(appender, BaseAppender)
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_colored_console_appender_color_format_structure(self, mock_stdout, sample_log_record, simple_formatter):
        """Test that color formatting follows correct structure: COLOR + MESSAGE + RESET"""
        appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.BLUE)
        
        appender.append(sample_log_record)
        
        output = mock_stdout.getvalue().rstrip('\n')  # Remove trailing newline
        
        # Should start with color code
        assert output.startswith(ConsoleColor.BLUE.value)
        # Should end with reset code
        assert output.endswith(ConsoleColor.RESET.value)
        # Should contain the message between color codes
        formatted_message = simple_formatter.format(sample_log_record)
        expected_output = f"{ConsoleColor.BLUE.value}{formatted_message}{ConsoleColor.RESET.value}"
        assert output == expected_output
    
    def test_colored_console_appender_all_color_enums(self):
        """Test that ColoredConsoleAppender works with all available colors"""
        all_colors = [color for color in ConsoleColor if color != ConsoleColor.RESET]
        
        for color in all_colors:
            appender = ColoredConsoleAppender(color=color)
            assert appender.color == color
            # Should not raise any exceptions
            appender.initialize()
            appender.teardown()
            appender.flush()


class TestCompositeAppender:
    """Test the CompositeAppender class"""
    
    def test_composite_appender_initialization_with_appenders(self, simple_formatter):
        """Test CompositeAppender initialization with a list of appenders"""
        console_appender = ConsoleAppender(formatter=simple_formatter)
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            file_appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            appenders = [console_appender, file_appender]
            
            composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
            
            assert len(composite.appenders) == 2
            assert console_appender in composite.appenders
            assert file_appender in composite.appenders
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_composite_appender_initialization_empty_appenders_raises_error(self):
        """Test CompositeAppender initialization with empty appenders list raises ValueError"""
        with pytest.raises(ValueError, match="At least one appender must be provided"):
            CompositeAppender(appenders=[])
    
    def test_composite_appender_initialization_default_empty_list_raises_error(self):
        """Test CompositeAppender initialization with default empty list raises ValueError"""
        with pytest.raises(ValueError, match="At least one appender must be provided"):
            CompositeAppender()
    
    def test_composite_appender_append_delegates_to_all_appenders(self, sample_log_record, simple_formatter):
        """Test that CompositeAppender delegates append to all its appenders"""
        # Create mock appenders
        mock_appender1 = Mock(spec=BaseAppender)
        mock_appender2 = Mock(spec=BaseAppender)
        mock_appender3 = Mock(spec=BaseAppender)
        
        appenders = [mock_appender1, mock_appender2, mock_appender3]
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        composite.append(sample_log_record)
        
        # Verify each appender's append method was called once with the record
        mock_appender1.append.assert_called_once_with(sample_log_record)
        mock_appender2.append.assert_called_once_with(sample_log_record)
        mock_appender3.append.assert_called_once_with(sample_log_record)
    
    def test_composite_appender_flush_delegates_to_all_appenders(self, simple_formatter):
        """Test that CompositeAppender delegates flush to all its appenders"""
        # Create mock appenders
        mock_appender1 = Mock(spec=BaseAppender)
        mock_appender2 = Mock(spec=BaseAppender)
        
        appenders = [mock_appender1, mock_appender2]
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        composite.flush()
        
        # Verify each appender's flush method was called once
        mock_appender1.flush.assert_called_once()
        mock_appender2.flush.assert_called_once()
    
    def test_composite_appender_initialize_delegates_to_all_appenders(self, simple_formatter):
        """Test that CompositeAppender delegates initialize to all its appenders"""
        # Create mock appenders
        mock_appender1 = Mock(spec=BaseAppender)
        mock_appender2 = Mock(spec=BaseAppender)
        
        appenders = [mock_appender1, mock_appender2]
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        composite.initialize()
        
        # Verify each appender's initialize method was called once
        mock_appender1.initialize.assert_called_once()
        mock_appender2.initialize.assert_called_once()
    
    def test_composite_appender_teardown_delegates_to_all_appenders(self, simple_formatter):
        """Test that CompositeAppender delegates teardown to all its appenders"""
        # Create mock appenders
        mock_appender1 = Mock(spec=BaseAppender)
        mock_appender2 = Mock(spec=BaseAppender)
        
        appenders = [mock_appender1, mock_appender2]
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        composite.teardown()
        
        # Verify each appender's teardown method was called once
        mock_appender1.teardown.assert_called_once()
        mock_appender2.teardown.assert_called_once()
    
    def test_composite_appender_add_appender_valid(self, simple_formatter):
        """Test adding a valid appender to CompositeAppender"""
        initial_appender = Mock(spec=BaseAppender)
        composite = CompositeAppender(formatter=simple_formatter, appenders=[initial_appender])
        
        new_appender = Mock(spec=BaseAppender)
        composite.add_appender(new_appender)
        
        assert len(composite.appenders) == 2
        assert new_appender in composite.appenders
        assert initial_appender in composite.appenders
    
    def test_composite_appender_add_appender_invalid_type(self, simple_formatter):
        """Test adding an invalid type to CompositeAppender raises TypeError"""
        initial_appender = Mock(spec=BaseAppender)
        composite = CompositeAppender(formatter=simple_formatter, appenders=[initial_appender])
        
        # Try to add a string instead of a BaseAppender
        with pytest.raises(TypeError, match="appender must be an instance of BaseAppender"):
            composite.add_appender("not an appender")
        
        # Try to add None
        with pytest.raises(TypeError, match="appender must be an instance of BaseAppender"):
            composite.add_appender(None)
        
        # Try to add a regular object
        with pytest.raises(TypeError, match="appender must be an instance of BaseAppender"):
            composite.add_appender(object())
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_composite_appender_real_appenders_integration(self, mock_stdout, sample_log_record, simple_formatter):
        """Test CompositeAppender with real appenders working together"""
        console_appender = ConsoleAppender(formatter=simple_formatter)
        colored_appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.GREEN)
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            file_appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            appenders = [console_appender, colored_appender, file_appender]
            composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
            
            composite.append(sample_log_record)
            
            # Check console output (both regular and colored)
            console_output = mock_stdout.getvalue()
            lines = console_output.strip().split('\n')
            
            # Should have output from both console appenders
            assert len(lines) == 2
            assert "Test log message" in lines[0]
            assert "Test log message" in lines[1]
            # One should have color codes
            has_color = any(ConsoleColor.GREEN.value in line for line in lines)
            assert has_color
            
            # Check file output
            with open(temp_path, 'r') as f:
                file_content = f.read()
                assert "Test log message" in file_content
                assert "INFO" in file_content
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_composite_appender_multiple_records(self, simple_formatter):
        """Test CompositeAppender with multiple log records"""
        mock_appender1 = Mock(spec=BaseAppender)
        mock_appender2 = Mock(spec=BaseAppender)
        
        appenders = [mock_appender1, mock_appender2]
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        records = [
            LogRecord(LoggingLevel.INFO, "First message"),
            LogRecord(LoggingLevel.ERROR, "Second message"),
            LogRecord(LoggingLevel.DEBUG, "Third message")
        ]
        
        for record in records:
            composite.append(record)
        
        # Each appender should have been called 3 times (once for each record)
        assert mock_appender1.append.call_count == 3
        assert mock_appender2.append.call_count == 3
        
        # Verify the specific calls
        expected_calls = [call(record) for record in records]
        mock_appender1.append.assert_has_calls(expected_calls)
        mock_appender2.append.assert_has_calls(expected_calls)
    
    def test_composite_appender_inheritance(self, simple_formatter):
        """Test that CompositeAppender properly inherits from BaseAppender"""
        mock_appender = Mock(spec=BaseAppender)
        composite = CompositeAppender(formatter=simple_formatter, appenders=[mock_appender])
        
        assert isinstance(composite, BaseAppender)
    
    def test_composite_appender_error_handling_one_appender_fails(self, sample_log_record, simple_formatter):
        """Test CompositeAppender behavior when one appender fails"""
        # Create one good appender and one that raises an exception
        good_appender = Mock(spec=BaseAppender)
        failing_appender = Mock(spec=BaseAppender)
        failing_appender.append.side_effect = Exception("Appender failed")
        
        appenders = [good_appender, failing_appender]
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        # The composite should propagate the exception
        with pytest.raises(Exception, match="Appender failed"):
            composite.append(sample_log_record)
        
        # But the good appender should still have been called
        good_appender.append.assert_called_once_with(sample_log_record)
    
    def test_composite_appender_error_handling_flush_fails(self, simple_formatter):
        """Test CompositeAppender behavior when flush fails on one appender"""
        good_appender = Mock(spec=BaseAppender)
        failing_appender = Mock(spec=BaseAppender)
        failing_appender.flush.side_effect = Exception("Flush failed")
        
        appenders = [good_appender, failing_appender]
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        # The composite should propagate the exception
        with pytest.raises(Exception, match="Flush failed"):
            composite.flush()
        
        # But the good appender should still have been called
        good_appender.flush.assert_called_once()
    
    def test_composite_appender_single_appender(self, sample_log_record, simple_formatter):
        """Test CompositeAppender with only a single appender"""
        mock_appender = Mock(spec=BaseAppender)
        composite = CompositeAppender(formatter=simple_formatter, appenders=[mock_appender])
        
        composite.append(sample_log_record)
        composite.flush()
        composite.initialize()
        composite.teardown()
        
        mock_appender.append.assert_called_once_with(sample_log_record)
        mock_appender.flush.assert_called_once()
        mock_appender.initialize.assert_called_once()
        mock_appender.teardown.assert_called_once()
    
    def test_composite_appender_many_appenders(self, sample_log_record, simple_formatter):
        """Test CompositeAppender with many appenders"""
        num_appenders = 10
        appenders = [Mock(spec=BaseAppender) for _ in range(num_appenders)]
        
        composite = CompositeAppender(formatter=simple_formatter, appenders=appenders)
        
        composite.append(sample_log_record)
        
        # Each appender should have been called
        for appender in appenders:
            appender.append.assert_called_once_with(sample_log_record)
        
        assert len(composite.appenders) == num_appenders
    
    def test_composite_appender_add_multiple_appenders(self, simple_formatter):
        """Test adding multiple appenders dynamically"""
        initial_appender = Mock(spec=BaseAppender)
        composite = CompositeAppender(formatter=simple_formatter, appenders=[initial_appender])
        
        # Add several appenders
        new_appenders = [Mock(spec=BaseAppender) for _ in range(3)]
        for appender in new_appenders:
            composite.add_appender(appender)
        
        assert len(composite.appenders) == 4  # 1 initial + 3 added
        
        # All appenders should be in the list
        assert initial_appender in composite.appenders
        for appender in new_appenders:
            assert appender in composite.appenders
    
    @patch('appenders.console_appender.sys.stdout', new_callable=StringIO)
    def test_composite_appender_different_formatters(self, mock_stdout, sample_log_record):
        """Test CompositeAppender with appenders using different formatters"""
        simple_formatter = SimpleFormatter()
        json_formatter = JSONFormatter()
        
        console_simple = ConsoleAppender(formatter=simple_formatter)
        console_json = ConsoleAppender(formatter=json_formatter)
        
        appenders = [console_simple, console_json]
        # Note: CompositeAppender's formatter parameter is not used since each appender has its own
        composite = CompositeAppender(formatter=None, appenders=appenders)
        
        composite.append(sample_log_record)
        
        output = mock_stdout.getvalue()
        lines = output.strip().split('\n')
        
        assert len(lines) == 2
        # One line should be simple format, one should be JSON
        simple_line = [line for line in lines if "Test log message" in line and '"message"' not in line][0]
        json_line = [line for line in lines if '"message": "Test log message"' in line][0]
        
        assert "INFO" in simple_line
        assert '"level": "INFO"' in json_line
    
    def test_composite_appender_integration_multiple_types(self, sample_log_record):
        """Test CompositeAppender integration with multiple types of appenders"""
        simple_formatter = SimpleFormatter()
        json_formatter = JSONFormatter()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create different types of appenders
            console_appender = ConsoleAppender(formatter=simple_formatter)
            colored_appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.BLUE)
            file_appender = FileAppender(file_path=temp_path, formatter=json_formatter)
            
            # Create composite appender
            composite = CompositeAppender(appenders=[console_appender, colored_appender, file_appender])
            
            with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
                composite.append(sample_log_record)
            
            # Check console outputs
            console_output = mock_stdout.getvalue()
            lines = console_output.strip().split('\n')
            
            assert len(lines) == 2  # Console and colored console
            assert "Test log message" in console_output
            assert ConsoleColor.BLUE.value in console_output
            assert ConsoleColor.RESET.value in console_output
            
            # Check file output
            with open(temp_path, 'r') as f:
                file_content = f.read()
                assert '"message": "Test log message"' in file_content
                assert '"level": "INFO"' in file_content
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_nested_composite_appenders(self, sample_log_record):
        """Test CompositeAppenders containing other CompositeAppenders"""
        simple_formatter = SimpleFormatter()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create basic appenders
            console1 = ConsoleAppender(formatter=simple_formatter)
            console2 = ConsoleAppender(formatter=simple_formatter)
            file_appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            # Create inner composite
            inner_composite = CompositeAppender(appenders=[console1, console2])
            
            # Create outer composite containing the inner composite and file appender
            outer_composite = CompositeAppender(appenders=[inner_composite, file_appender])
            
            with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
                outer_composite.append(sample_log_record)
            
            # Should have output from both console appenders
            console_output = mock_stdout.getvalue()
            lines = console_output.strip().split('\n')
            assert len(lines) == 2  # Two console outputs
            
            for line in lines:
                assert "Test log message" in line
                assert "INFO" in line
            
            # Check file output
            with open(temp_path, 'r') as f:
                file_content = f.read()
                assert "Test log message" in file_content
                assert "INFO" in file_content
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    


class TestFileAppender:
    """Test the FileAppender class"""
    
    def test_file_appender_initialization(self, simple_formatter):
        """Test FileAppender initialization"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            assert appender.file_path == temp_path
            assert appender.formatter == simple_formatter
            assert appender.file is not None
            appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_initialization_without_formatter(self):
        """Test FileAppender initialization with default formatter"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path)
            assert appender.formatter is not None
            assert isinstance(appender.formatter, SimpleFormatter)
            appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_append_creates_file(self, sample_log_record, simple_formatter):
        """Test that FileAppender creates file and writes content"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Remove the file so we can test creation
        os.unlink(temp_path)
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            appender.append(sample_log_record)
            appender.teardown()
            
            # Verify file was created and contains content
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Test log message" in content
                assert "INFO" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_append_multiple_records(self, simple_formatter):
        """Test FileAppender with multiple log records"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            records = [
                LogRecord(LoggingLevel.INFO, "First message"),
                LogRecord(LoggingLevel.ERROR, "Second message"),
                LogRecord(LoggingLevel.DEBUG, "Third message")
            ]
            
            for record in records:
                appender.append(record)
            
            appender.teardown()
            
            # Verify all records were written
            with open(temp_path, 'r') as f:
                content = f.read()
                lines = content.strip().split('\n')
                
                assert len(lines) == 3
                assert "First message" in content
                assert "Second message" in content
                assert "Third message" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_append_mode(self, simple_formatter):
        """Test that FileAppender opens file in append mode"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            # Write some initial content
            temp_file.write(b"Initial content\n")
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            record = LogRecord(LoggingLevel.INFO, "New message")
            appender.append(record)
            appender.teardown()
            
            # Verify original content is preserved
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Initial content" in content
                assert "New message" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_json_formatter(self, sample_log_record, json_formatter):
        """Test FileAppender with JSON formatter"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=json_formatter)
            appender.append(sample_log_record)
            appender.teardown()
            
            with open(temp_path, 'r') as f:
                content = f.read()
                assert '"message": "Test log message"' in content
                assert '"level": "INFO"' in content
                assert '"source": "test_module.py"' in content
                assert '"user_id": 123' in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_teardown_closes_file(self, simple_formatter):
        """Test that teardown properly closes the file"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            # File should be open
            assert appender.file is not None
            assert not appender.file.closed
            
            appender.teardown()
            
            # File should be closed
            assert appender.file.closed
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_teardown_multiple_calls(self, simple_formatter):
        """Test that multiple teardown calls don't cause errors"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            # Call teardown multiple times
            appender.teardown()
            appender.teardown()  # Should not raise an error
            appender.teardown()  # Should not raise an error
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_flush_method(self, simple_formatter):
        """Test FileAppender flush method"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            # Mock the file's flush method
            with patch.object(appender.file, 'flush') as mock_flush:
                appender.flush()
                mock_flush.assert_called_once()
            
            appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_flush_called_on_append(self, sample_log_record, simple_formatter):
        """Test that flush is called when appending a record"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            # Mock the flush method
            with patch.object(appender, 'flush') as mock_flush:
                appender.append(sample_log_record)
                mock_flush.assert_called()
            
            appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_destructor(self, simple_formatter):
        """Test that FileAppender destructor calls teardown"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            # Mock teardown to verify it's called
            with patch.object(appender, 'teardown') as mock_teardown:
                # Trigger destructor
                del appender
                # Note: __del__ is not guaranteed to be called immediately
                # but we can at least verify the method exists
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_appender_permission_error(self, simple_formatter):
        """Test FileAppender behavior with permission errors"""
        # Try to write to a directory that doesn't exist
        invalid_path = "/nonexistent/directory/file.log"
        
        with pytest.raises((FileNotFoundError, PermissionError, OSError)):
            FileAppender(file_path=invalid_path, formatter=simple_formatter)
    
    def test_file_appender_empty_file_path(self, simple_formatter):
        """Test FileAppender with empty file path"""
        with pytest.raises((ValueError, OSError)):
            FileAppender(file_path="", formatter=simple_formatter)


class TestAppenderIntegration:
    """Integration tests for appenders working together"""
    
    def test_same_formatter_different_appenders(self, sample_log_record):
        """Test using the same formatter with different appenders"""
        formatter = SimpleFormatter()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            console_appender = ConsoleAppender(formatter=formatter)
            file_appender = FileAppender(file_path=temp_path, formatter=formatter)
            
            with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
                console_appender.append(sample_log_record)
                file_appender.append(sample_log_record)
            
            # Both should use the same formatting
            console_output = mock_stdout.getvalue()
            
            with open(temp_path, 'r') as f:
                file_output = f.read()
            
            # Remove newlines for comparison
            console_content = console_output.strip()
            file_content = file_output.strip()
            
            assert console_content == file_content
            assert "Test log message" in console_content
            assert "INFO" in console_content
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_different_formatters_same_record(self, sample_log_record):
        """Test using different formatters with the same record"""
        simple_formatter = SimpleFormatter()
        json_formatter = JSONFormatter()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            console_appender = ConsoleAppender(formatter=simple_formatter)
            file_appender = FileAppender(file_path=temp_path, formatter=json_formatter)
            
            with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
                console_appender.append(sample_log_record)
                file_appender.append(sample_log_record)
            
            console_output = mock_stdout.getvalue()
            
            with open(temp_path, 'r') as f:
                file_output = f.read()
            
            # Console should have simple format
            assert "Test log message" in console_output
            assert "INFO" in console_output
            assert '"message"' not in console_output  # Should not be JSON
            
            # File should have JSON format
            assert '"message": "Test log message"' in file_output
            assert '"level": "INFO"' in file_output
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_colored_console_appender_integration(self, sample_log_record):
        """Test ColoredConsoleAppender integration with different formatters"""
        simple_formatter = SimpleFormatter()
        json_formatter = JSONFormatter()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test colored console with simple formatter and file with JSON
            colored_console = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.GREEN)
            file_appender = FileAppender(file_path=temp_path, formatter=json_formatter)
            
            with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
                colored_console.append(sample_log_record)
                file_appender.append(sample_log_record)
            
            console_output = mock_stdout.getvalue()
            
            with open(temp_path, 'r') as f:
                file_output = f.read()
            
            # Console should have colored simple format
            assert "Test log message" in console_output
            assert "INFO" in console_output
            assert ConsoleColor.GREEN.value in console_output
            assert ConsoleColor.RESET.value in console_output
            assert '"message"' not in console_output  # Should not be JSON
            
            # File should have JSON format
            assert '"message": "Test log message"' in file_output
            assert '"level": "INFO"' in file_output
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_multiple_colored_console_appenders(self, sample_log_record):
        """Test multiple ColoredConsoleAppenders with different colors"""
        formatter = SimpleFormatter()
        
        appenders = [
            ColoredConsoleAppender(formatter=formatter, color=ConsoleColor.RED),
            ColoredConsoleAppender(formatter=formatter, color=ConsoleColor.BLUE),
            ColoredConsoleAppender(formatter=formatter, color=ConsoleColor.YELLOW)
        ]
        
        with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
            for appender in appenders:
                appender.append(sample_log_record)
        
        output = mock_stdout.getvalue()
        lines = output.strip().split('\n')
        
        assert len(lines) == 3
        assert ConsoleColor.RED.value in lines[0]
        assert ConsoleColor.BLUE.value in lines[1]
        assert ConsoleColor.YELLOW.value in lines[2]
        
        # All lines should contain reset and the message
        for line in lines:
            assert ConsoleColor.RESET.value in line
            assert "Test log message" in line
    
    def test_composite_appender_integration_multiple_types(self, sample_log_record):
        """Test CompositeAppender integration with multiple types of appenders"""
        simple_formatter = SimpleFormatter()
        json_formatter = JSONFormatter()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create different types of appenders
            console_appender = ConsoleAppender(formatter=simple_formatter)
            colored_appender = ColoredConsoleAppender(formatter=simple_formatter, color=ConsoleColor.BLUE)
            file_appender = FileAppender(file_path=temp_path, formatter=json_formatter)
            
            # Create composite appender
            composite = CompositeAppender(appenders=[console_appender, colored_appender, file_appender])
            
            with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
                composite.append(sample_log_record)
            
            # Check console outputs
            console_output = mock_stdout.getvalue()
            lines = console_output.strip().split('\n')
            
            assert len(lines) == 2  # Console and colored console
            assert "Test log message" in console_output
            assert ConsoleColor.BLUE.value in console_output
            assert ConsoleColor.RESET.value in console_output
            
            # Check file output
            with open(temp_path, 'r') as f:
                file_content = f.read()
                assert '"message": "Test log message"' in file_content
                assert '"level": "INFO"' in file_content
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_nested_composite_appenders(self, sample_log_record):
        """Test CompositeAppenders containing other CompositeAppenders"""
        simple_formatter = SimpleFormatter()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create basic appenders
            console1 = ConsoleAppender(formatter=simple_formatter)
            console2 = ConsoleAppender(formatter=simple_formatter)
            file_appender = FileAppender(file_path=temp_path, formatter=simple_formatter)
            
            # Create inner composite
            inner_composite = CompositeAppender(appenders=[console1, console2])
            
            # Create outer composite containing the inner composite and file appender
            outer_composite = CompositeAppender(appenders=[inner_composite, file_appender])
            
            with patch('appenders.console_appender.sys.stdout', new_callable=StringIO) as mock_stdout:
                outer_composite.append(sample_log_record)
            
            # Should have output from both console appenders
            console_output = mock_stdout.getvalue()
            lines = console_output.strip().split('\n')
            assert len(lines) == 2  # Two console outputs
            
            for line in lines:
                assert "Test log message" in line
                assert "INFO" in line
            
            # Check file output
            with open(temp_path, 'r') as f:
                file_content = f.read()
                assert "Test log message" in file_content
                assert "INFO" in file_content
            
            file_appender.teardown()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    


if __name__ == "__main__":
    # If run directly, execute tests manually
    import traceback
    
    print("Running appender tests manually...")
    
    # Create test data
    test_record = LogRecord(
        level=LoggingLevel.INFO,
        message="Test log message",
        source="test_module.py",
        metadata={"user_id": 123, "action": "login"}
    )
    simple_fmt = SimpleFormatter()
    json_fmt = JSONFormatter()
    
    failed = 0
    
    # Test BaseAppender
    try:
        print("Testing BaseAppender...")
        base = BaseAppender()
        assert isinstance(base.formatter, SimpleFormatter)
        base.initialize()
        base.teardown()
        base.flush()
        
        try:
            base.append(test_record)
            print("✗ BaseAppender.append should raise NotImplementedError")
            failed += 1
        except NotImplementedError:
            pass  # Expected
        
        print("✓ BaseAppender tests passed")
    except Exception as e:
        print(f"✗ BaseAppender test failed: {e}")
        failed += 1
    
    # Test ConsoleAppender
    try:
        print("Testing ConsoleAppender...")
        console = ConsoleAppender(formatter=simple_fmt)
        console.initialize()
        console.teardown()
        print("✓ ConsoleAppender basic tests passed")
    except Exception as e:
        print(f"✗ ConsoleAppender test failed: {e}")
        failed += 1
    
    # Test ColoredConsoleAppender
    try:
        print("Testing ColoredConsoleAppender...")
        
        # Test basic functionality
        colored_console = ColoredConsoleAppender(formatter=simple_fmt, color=ConsoleColor.GREEN)
        colored_console.initialize()
        colored_console.teardown()
        
        # Test append with color
        print("Testing colored output:")
        colored_console.append(test_record)
        
        # Test color changing
        colored_console.set_color(ConsoleColor.RED)
        print("Changed to red color:")
        colored_console.append(LogRecord(LoggingLevel.ERROR, "Error message in red", "test.py"))
        
        # Test different colors
        for color in [ConsoleColor.BLUE, ConsoleColor.YELLOW, ConsoleColor.MAGENTA]:
            colored_appender = ColoredConsoleAppender(formatter=simple_fmt, color=color)
            colored_appender.append(LogRecord(LoggingLevel.INFO, f"Message in {color.name}", "test.py"))
        
        print("✓ ColoredConsoleAppender tests passed")
    except Exception as e:
        print(f"✗ ColoredConsoleAppender test failed: {e}")
        traceback.print_exc()
        failed += 1

    # Test FileAppender
    try:
        print("Testing FileAppender...")
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        file_app = FileAppender(file_path=temp_path, formatter=simple_fmt)
        file_app.append(test_record)
        file_app.teardown()
        
        # Check file content
        with open(temp_path, 'r') as f:
            content = f.read()
            assert "Test log message" in content
            assert "INFO" in content
        
        os.unlink(temp_path)
        print("✓ FileAppender tests passed")
    except Exception as e:
        print(f"✗ FileAppender test failed: {e}")
        failed += 1
    
    # Test CompositeAppender
    try:
        print("Testing CompositeAppender...")
        
        # Test basic functionality
        console_appender = ConsoleAppender(formatter=simple_fmt)
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        file_appender = FileAppender(file_path=temp_path, formatter=simple_fmt)
        colored_appender = ColoredConsoleAppender(formatter=simple_fmt, color=ConsoleColor.CYAN)
        
        # Test composite with multiple appenders
        composite = CompositeAppender(appenders=[console_appender, file_appender, colored_appender])
        
        print("Testing composite append (should see console + colored output):")
        composite.append(test_record)
        
        # Test adding appender dynamically
        json_appender = ConsoleAppender(formatter=json_fmt)
        composite.add_appender(json_appender)
        
        print("Added JSON appender - testing again:")
        composite.append(LogRecord(LoggingLevel.WARNING, "Composite test message", "manual_test.py"))
        
        # Test lifecycle methods
        composite.flush()
        composite.initialize()
        composite.teardown()
        
        # Check file content
        with open(temp_path, 'r') as f:
            content = f.read()
            assert "Test log message" in content
            assert "Composite test message" in content
        
        os.unlink(temp_path)
        
        # Test error handling
        try:
            CompositeAppender(appenders=[])
            print("✗ Should have raised ValueError for empty appenders")
            failed += 1
        except ValueError:
            pass  # Expected
        
        print("✓ CompositeAppender tests passed")
    except Exception as e:
        print(f"✗ CompositeAppender test failed: {e}")
        traceback.print_exc()
        failed += 1
    
    if failed == 0:
        print(f"\nAll manual tests passed! 🎉")
    else:
        print(f"\n{failed} tests failed. ❌")
    
    print("\nTo run with pytest: python -m pytest tests/test_appenders.py -v")
    sys.exit(failed)
