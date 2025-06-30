# Appenders package
from .base_appender import BaseAppender
from .console_appender import ConsoleAppender, ColoredConsoleAppender
from .file_appender import FileAppender
from .composite_appender import CompositeAppender
from .sqlite_appender import SQLiteAppender 
from .mysql_appender import MySQLAppender
from typing import Dict

all_appender_strings: Dict[str, type]  = {
    "ConsoleAppender": ConsoleAppender,
    "console": ConsoleAppender,
    "ColoredConsoleAppender": ColoredConsoleAppender,
    "coloredconsole": ColoredConsoleAppender,
    "FileAppender": FileAppender,
    "file": FileAppender,
    "SQLiteAppender": SQLiteAppender,
    "sqlite": SQLiteAppender,
    "MySQLAppender": MySQLAppender,
    "mysql": MySQLAppender
}

__all__ = [
    "BaseAppender",
    "ConsoleAppender", 
    "ColoredConsoleAppender",
    "FileAppender",
    "CompositeAppender",
    "SQLiteAppender",
    "MySQLAppender"
]
