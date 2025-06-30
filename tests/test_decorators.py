#!/usr/bin/env python3
"""
Test suite for decorator functionality.

This module tests all decorator functionality including:
- Basic decorator operations
- Custom logger parameter support
- Function call logging
- Timing and performance monitoring
- Error handling
- Decorator combinations
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, call

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decorators import (
    logged,
    timed,
    performance_monitor,
    debug_logged,
    error_handler,
    combine_decorators,
)
from managers.global_manager import GlobalManager
from core.level import LoggingLevel
from core.logger import Logger
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ConsoleAppender


class TestDecoratorBasics:
    """Test basic decorator functionality."""

    @patch.object(GlobalManager, "get_global_logger")
    def test_logged_decorator_basic(self, mock_get_global):
        """Test basic logged decorator functionality."""
        mock_logger = Mock()
        mock_get_global.return_value = mock_logger

        @logged()
        def add_numbers(a, b):
            return a + b

        result = add_numbers(5, 3)

        assert result == 8
        assert mock_logger.log.call_count >= 2  # Call and result logs
        mock_logger.error.assert_not_called()

    @patch.object(GlobalManager, "get_global_logger")
    def test_timed_decorator_basic(self, mock_get_global):
        """Test basic timed decorator functionality."""
        mock_logger = Mock()
        mock_get_global.return_value = mock_logger

        @timed()
        def quick_function():
            return "done"

        result = quick_function()

        assert result == "done"
        mock_logger.log.assert_called_once()
        # Check that timing message was logged
        call_args = mock_logger.log.call_args[0]
        assert "executed in" in call_args[1]

    @patch.object(GlobalManager, "get_global_logger")
    def test_performance_monitor_basic(self, mock_get_global):
        """Test basic performance monitor decorator."""
        mock_logger = Mock()
        mock_get_global.return_value = mock_logger

        @performance_monitor()
        def monitored_function():
            return "monitored"

        result = monitored_function()

        assert result == "monitored"
        assert mock_logger.log.call_count == 2  # ENTER and EXIT

        # Check ENTER and EXIT messages
        enter_call = mock_logger.log.call_args_list[0][0]
        exit_call = mock_logger.log.call_args_list[1][0]
        assert "ENTER: monitored_function" in enter_call[1]
        assert "EXIT: monitored_function (success" in exit_call[1]


class TestCustomLoggerParameter:
    """Test decorators with custom logger parameter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.custom_logger = Mock()
        self.custom_logger.log = Mock()
        self.custom_logger.error = Mock()

    @patch.object(GlobalManager, "get_global_logger")
    def test_logged_with_custom_logger(self, mock_get_global):
        """Test logged decorator with custom logger."""
        mock_global_logger = Mock()
        mock_get_global.return_value = mock_global_logger

        @logged(logger=self.custom_logger)
        def custom_logged_function(x):
            return x * 2

        result = custom_logged_function(5)

        assert result == 10
        # Custom logger should be used, not global
        assert self.custom_logger.log.call_count >= 2
        mock_global_logger.log.assert_not_called()

    @patch.object(GlobalManager, "get_global_logger")
    def test_timed_with_custom_logger(self, mock_get_global):
        """Test timed decorator with custom logger."""
        mock_global_logger = Mock()
        mock_get_global.return_value = mock_global_logger

        @timed(logger=self.custom_logger)
        def custom_timed_function():
            time.sleep(0.01)  # 10ms
            return "timed"

        result = custom_timed_function()

        assert result == "timed"
        # Custom logger should be used, not global
        self.custom_logger.log.assert_called_once()
        mock_global_logger.log.assert_not_called()

    @patch.object(GlobalManager, "get_global_logger")
    def test_performance_monitor_with_custom_logger(self, mock_get_global):
        """Test performance monitor with custom logger."""
        mock_global_logger = Mock()
        mock_get_global.return_value = mock_global_logger

        @performance_monitor(logger=self.custom_logger)
        def custom_perf_function():
            return "performance"

        result = custom_perf_function()

        assert result == "performance"
        # Custom logger should be used, not global
        assert self.custom_logger.log.call_count == 2  # ENTER and EXIT
        mock_global_logger.log.assert_not_called()

    @patch.object(GlobalManager, "get_global_logger")
    def test_error_handler_with_custom_logger(self, mock_get_global):
        """Test error handler with custom logger."""
        mock_global_logger = Mock()
        mock_get_global.return_value = mock_global_logger

        @error_handler(reraise=False, logger=self.custom_logger)
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()

        assert result is None  # Function returns None when reraise=False
        # Custom logger should be used, not global
        self.custom_logger.log.assert_called_once()
        mock_global_logger.log.assert_not_called()

        # Check error message
        call_args = self.custom_logger.log.call_args[0]
        assert "Exception in 'failing_function'" in call_args[1]


class TestDebugLoggedDecorator:
    """Test debug_logged decorator variations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.custom_logger = Mock()

    @patch.object(GlobalManager, "get_global_logger")
    def test_debug_logged_without_args(self, mock_get_global):
        """Test @debug_logged used without parentheses."""
        mock_global_logger = Mock()
        mock_get_global.return_value = mock_global_logger

        @debug_logged
        def simple_debug_function():
            return "debug"

        result = simple_debug_function()

        assert result == "debug"
        assert mock_global_logger.log.call_count >= 2  # Call and result logs

    @patch.object(GlobalManager, "get_global_logger")
    def test_debug_logged_with_custom_logger(self, mock_get_global):
        """Test @debug_logged() with custom logger."""
        mock_global_logger = Mock()
        mock_get_global.return_value = mock_global_logger

        @debug_logged(logger=self.custom_logger)
        def custom_debug_function():
            return "custom debug"

        result = custom_debug_function()

        assert result == "custom debug"
        # Custom logger should be used
        assert self.custom_logger.log.call_count >= 2
        mock_global_logger.log.assert_not_called()


class TestDecoratorParameters:
    """Test decorator parameter variations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.custom_logger = Mock()

    @patch.object(GlobalManager, "get_global_logger")
    def test_logged_with_all_parameters(self, mock_get_global):
        """Test logged decorator with all parameters."""
        mock_get_global.return_value = Mock()

        @logged(
            level=LoggingLevel.WARNING,
            message="Custom message",
            include_args=False,
            include_result=False,
            logger=self.custom_logger,
        )
        def fully_configured_function(a, b):
            return a + b

        result = fully_configured_function(1, 2)

        assert result == 3
        # Should only log the custom message, not args or result
        self.custom_logger.log.assert_called_once()
        call_args = self.custom_logger.log.call_args[0]
        assert call_args[0] == LoggingLevel.WARNING
        assert "Custom message" in call_args[1]

    @patch.object(GlobalManager, "get_global_logger")
    def test_timed_with_threshold_and_custom_logger(self, mock_get_global):
        """Test timed decorator with threshold and custom logger."""
        mock_get_global.return_value = Mock()

        @timed(threshold_ms=50, logger=self.custom_logger)
        def fast_function():
            return "fast"

        result = fast_function()

        assert result == "fast"
        # Should not log because execution time is below threshold
        self.custom_logger.log.assert_not_called()

    @patch.object(GlobalManager, "get_global_logger")
    def test_error_handler_reraise_with_custom_logger(self, mock_get_global):
        """Test error handler with reraise=True and custom logger."""
        mock_get_global.return_value = Mock()

        @error_handler(reraise=True, logger=self.custom_logger)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

        # Should still log the error
        self.custom_logger.log.assert_called_once()


class TestDecoratorCombinations:
    """Test combining decorators with custom loggers."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger1 = Mock()
        self.logger2 = Mock()

    @patch.object(GlobalManager, "get_global_logger")
    def test_combine_decorators_same_logger(self, mock_get_global):
        """Test combining decorators with the same custom logger."""
        mock_get_global.return_value = Mock()

        @combine_decorators(logged(logger=self.logger1), timed(logger=self.logger1))
        def combined_function():
            return "combined"

        result = combined_function()

        assert result == "combined"
        # Both decorators should use the same custom logger
        assert self.logger1.log.call_count >= 3  # logged calls + timed call
        self.logger2.log.assert_not_called()

    @patch.object(GlobalManager, "get_global_logger")
    def test_combine_decorators_different_loggers(self, mock_get_global):
        """Test combining decorators with different custom loggers."""
        mock_get_global.return_value = Mock()

        @combine_decorators(logged(logger=self.logger1), timed(logger=self.logger2))
        def multi_logger_function():
            return "multi"

        result = multi_logger_function()

        assert result == "multi"
        # Each decorator should use its own logger
        assert self.logger1.log.call_count >= 2  # logged decorator
        self.logger2.log.assert_called_once()  # timed decorator


class TestRealLoggerIntegration:
    """Test decorators with real logger instances."""

    def setup_method(self, method):
        """Set up real logger for integration testing."""
        # Create a real logger with console appender for testing
        # Use method name to ensure unique logger names
        logger_name = f"test_decorator_logger_{method.__name__}"
        console_appender = ConsoleAppender()
        self.real_logger = (
            LoggerBuilder()
            .set_name(logger_name)
            .set_level(LoggingLevel.DEBUG)
            .add_appender(console_appender)
            .build()
        )

    def test_logged_with_real_logger(self):
        """Test logged decorator with a real logger instance."""

        @logged(level=LoggingLevel.INFO, logger=self.real_logger)
        def real_logger_function(x, y):
            return x + y

        # This should work without errors and log to console
        result = real_logger_function(10, 20)
        assert result == 30

    def test_performance_monitor_with_real_logger(self):
        """Test performance monitor with a real logger instance."""

        @performance_monitor(level=LoggingLevel.DEBUG, logger=self.real_logger)
        def monitored_calculation():
            return sum(range(100))

        # This should work without errors and log to console
        result = monitored_calculation()
        assert result == 4950


class TestErrorConditions:
    """Test decorator error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.custom_logger = Mock()

    @patch.object(GlobalManager, "get_global_logger")
    def test_logged_decorator_with_exception(self, mock_get_global):
        """Test logged decorator when function raises exception."""
        mock_get_global.return_value = Mock()

        @logged(logger=self.custom_logger)
        def failing_function():
            raise RuntimeError("Function failed")

        with pytest.raises(RuntimeError, match="Function failed"):
            failing_function()

        # Should log the function call and the error
        assert self.custom_logger.log.call_count >= 1  # Function call
        self.custom_logger.error.assert_called_once()

    @patch.object(GlobalManager, "get_global_logger")
    def test_performance_monitor_with_exception(self, mock_get_global):
        """Test performance monitor when function raises exception."""
        mock_get_global.return_value = Mock()

        @performance_monitor(logger=self.custom_logger)
        def failing_monitored_function():
            raise ValueError("Monitored failure")

        with pytest.raises(ValueError, match="Monitored failure"):
            failing_monitored_function()

        # Should log ENTER and EXIT with exception info
        assert self.custom_logger.log.call_count == 2
        enter_call = self.custom_logger.log.call_args_list[0][0]
        exit_call = self.custom_logger.log.call_args_list[1][0]
        assert "ENTER:" in enter_call[1]
        assert "EXIT:" in exit_call[1] and "exception:" in exit_call[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
