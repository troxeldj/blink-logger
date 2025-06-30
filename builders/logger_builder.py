from core.logger import Logger
from typing import Optional, TYPE_CHECKING
from appenders.base_appender import BaseAppender
from core.level import LoggingLevel
from utils.dec import throws
from managers.global_manager import GlobalManager

if TYPE_CHECKING:
    from formatters.base_formatter import BaseFormatter
    from core.color import ConsoleColor


class LoggerBuilder:
    def __init__(self):
        self.name: Optional[str] = None
        self.level: Optional[LoggingLevel] = None
        self.appenders: list[BaseAppender] = []

    @throws(TypeError)
    def set_name(self, name: str):
        """Set the name of the logger."""
        if not isinstance(name, str):
            raise TypeError("name must be a string.")
        self.name = name
        return self

    @throws(TypeError)
    def set_level(self, level: LoggingLevel):
        """Set the logging level for the logger."""
        if not isinstance(level, LoggingLevel):
            raise TypeError("level must be an instance of LoggingLevel.")
        self.level = level
        return self

    @throws(TypeError)
    def add_appender(self, appender: BaseAppender):
        """Add an appender to the logger."""
        if not isinstance(appender, BaseAppender):
            raise TypeError("appender must be an instance of BaseAppender.")
        self.appenders.append(appender)
        return self

    @throws(TypeError)
    def add_console_appender(self, formatter: Optional["BaseFormatter"] = None):
        """Add a console appender with the given formatter."""
        from appenders.console_appender import ConsoleAppender

        if formatter is None:
            from formatters.simple_formatter import SimpleFormatter

            formatter = SimpleFormatter()
        appender = ConsoleAppender(formatter)
        return self.add_appender(appender)

    @throws(TypeError)
    def add_colored_console_appender(
        self,
        formatter: Optional["BaseFormatter"] = None,
        color: Optional["ConsoleColor"] = None,
    ):
        """Add a colored console appender with the given formatter and color."""
        from appenders.console_appender import ColoredConsoleAppender
        from core.color import ConsoleColor

        if formatter is None:
            from formatters.simple_formatter import SimpleFormatter

            formatter = SimpleFormatter()
        if color is None:
            color = ConsoleColor.DEFAULT
        appender = ColoredConsoleAppender(formatter, color)
        return self.add_appender(appender)

    @throws(TypeError)
    def add_file_appender(
        self, file_path: str, formatter: Optional["BaseFormatter"] = None
    ):
        """Add a file appender with the given formatter."""
        from appenders.file_appender import FileAppender

        if formatter is None:
            from formatters.simple_formatter import SimpleFormatter

            formatter = SimpleFormatter()
        appender = FileAppender(file_path, formatter)
        return self.add_appender(appender)

    @throws(ValueError)
    def build(self) -> Logger:
        """Build and return the Logger instance."""
        if not self.name:
            raise ValueError("Logger name must be set.")
        if not self.appenders:
            raise ValueError("At least one appender must be added to the logger.")
        loggerRet = Logger(name=self.name, level=self.level, appenders=self.appenders)
        # Note: Logger constructor already registers with GlobalManager
        return loggerRet
