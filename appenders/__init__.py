# Appenders package
from .base_appender import BaseAppender
from .console_appender import ConsoleAppender, ColoredConsoleAppender
from .file_appender import FileAppender
from .composite_appender import CompositeAppender
from .sqlite_appender import SQLiteAppender 
from typing import Dict

all_appender_strings: Dict[str, type]  = {
    "ConsoleAppender": ConsoleAppender,
    "ColoredConsoleAppender": ColoredConsoleAppender,
    "FileAppender": FileAppender,
    "SQLiteAppender": SQLiteAppender
}

__all__ = [
    "BaseAppender",
    "ConsoleAppender", 
    "ColoredConsoleAppender",
    "FileAppender",
    "CompositeAppender",
    "SQLiteAppender"
]
