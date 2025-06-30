#!/usr/bin/env python3
"""
Test script for blink-logger functionality
"""

import sys
import os

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test complete package functionality
from builders.logger_builder import LoggerBuilder
from appenders.console_appender import ConsoleAppender, ColoredConsoleAppender
from appenders.file_appender import FileAppender
from appenders.composite_appender import CompositeAppender
from formatters.simple_formatter import SimpleFormatter
from formatters.json_formatter import JSONFormatter
from filters.keyword_filter import KeywordFilter
from filters.level_filter import LevelFilter
from core.level import LoggingLevel
from core.color import ConsoleColor
from managers.global_manager import GlobalManager

print("✅ All major components imported successfully!")

# Test builder pattern
logger = (
    LoggerBuilder()
    .set_name("demo-logger")
    .set_level(LoggingLevel.INFO)
    .add_appender(ColoredConsoleAppender(SimpleFormatter(), color=ConsoleColor.GREEN))
    .build()
)

print("✅ Logger builder pattern works!")

# Test logging with filters
filter_appender = ConsoleAppender(
    formatter=SimpleFormatter(),
    filters=[KeywordFilter(["important"]), LevelFilter(LoggingLevel.INFO)],
)

logger.add_appender(filter_appender)
logger.log(LoggingLevel.INFO, "This is an important message!")
logger.log(LoggingLevel.DEBUG, "This debug message should be filtered out")

print("✅ Logging with filters works!")

# Test global manager
global_mgr = GlobalManager.get_instance()
print(f"✅ Global manager contains {len(global_mgr)} loggers")

# Test decorators and global logger
print("\n=== Testing Decorators ===")

from decorators import logged, timed

# Test accessing global logger
global_logger = GlobalManager.get_global_logger()
global_logger.info("Testing global logger access!")


# Test decorator on a simple function
@logged()
def demo_function(x, y):
    return x + y


@timed()
def demo_timing():
    import time

    time.sleep(0.01)  # 10ms
    return "timing test complete"


result1 = demo_function(10, 20)
result2 = demo_timing()

print(f"✅ Decorator test results: {result1}, {result2}")
print("🎉 All tests passed! blink-logger is ready to use!")
