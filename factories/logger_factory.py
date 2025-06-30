from core.logger import Logger
from appenders.base_appender import BaseAppender
from core.level import LoggingLevel
from utils.dec import throws
from core.color import ConsoleColor
from typing import List


class LoggerFactory:
  """Factory class for creating Logger instances."""

  @staticmethod
  def create_logger(
    name: str, level: LoggingLevel, appenders: List[BaseAppender]
  ) -> Logger:
    """
    Create a Logger instance with the specified name, level, and appenders.

    :param name: The name of the logger.
    :param level: The logging level.
    :param appenders: A list of BaseAppender instances to handle log output.
    :return: An instance of Logger.
    """
    return Logger(name=name, level=level, appenders=appenders)

  @staticmethod
  def create_simple_logger(
    name: str, level: LoggingLevel, appenders: List[BaseAppender]
  ) -> Logger:
    """
    Create a simple Logger instance with the specified name, level, and appenders.

    Note: This method assumes appenders already have appropriate formatters configured.

    :param name: The name of the logger.
    :param level: The logging level.
    :param appenders: A list of BaseAppender instances to handle log output.
    :return: An instance of Logger.
    """
    return Logger(name=name, level=level, appenders=appenders)

  @staticmethod
  def create_json_logger(
    name: str, level: LoggingLevel, appenders: List[BaseAppender]
  ) -> Logger:
    """
    Create a JSON Logger instance with the specified name, level, and appenders.

    Note: This method assumes appenders already have appropriate formatters configured.

    :param name: The name of the logger.
    :param level: The logging level.
    :param appenders: A list of BaseAppender instances to handle log output.
    :return: An instance of Logger.
    """
    return Logger(name=name, level=level, appenders=appenders)

  @staticmethod
  def create_console_logger(name: str, level: LoggingLevel) -> Logger:
    """
    Create a console Logger instance with the specified name and level.

    :param name: The name of the logger.
    :param level: The logging level.
    :return: An instance of Logger with a ConsoleAppender and SimpleFormatter.
    """
    from appenders.console_appender import ConsoleAppender
    from formatters.simple_formatter import SimpleFormatter

    appender = ConsoleAppender(formatter=SimpleFormatter())
    return LoggerFactory.create_simple_logger(name, level, [appender])

  @staticmethod
  def create_colored_console_logger(
    name: str, level: LoggingLevel, color: ConsoleColor
  ) -> Logger:
    """
    Create a colored console Logger instance with the specified name and level.

    :param name: The name of the logger.
    :param level: The logging level.
    :param color: The console color for output.
    :return: An instance of Logger with a ColoredConsoleAppender and SimpleFormatter.
    """
    from appenders.console_appender import ColoredConsoleAppender
    from formatters.simple_formatter import SimpleFormatter

    appender = ColoredConsoleAppender(formatter=SimpleFormatter(), color=color)
    return LoggerFactory.create_simple_logger(name, level, [appender])

  @staticmethod
  @throws(TypeError)
  def create_file_logger(name: str, level: LoggingLevel, file_path: str) -> Logger:
    """
    Create a file Logger instance with the specified name, level, and file path.

    :param name: The name of the logger.
    :param level: The logging level.
    :param file_path: The path to the log file.
    :return: An instance of Logger with a FileAppender and SimpleFormatter.
    """
    from appenders.file_appender import FileAppender
    from formatters.simple_formatter import SimpleFormatter

    appender = FileAppender(file_path=file_path, formatter=SimpleFormatter())
    return LoggerFactory.create_simple_logger(name, level, [appender])

  @staticmethod
  @throws(TypeError)
  def create_composite_logger(
    name: str, level: LoggingLevel, appenders: List[BaseAppender]
  ) -> Logger:
    """
    Create a composite Logger instance with the specified name, level, and appenders.

    :param name: The name of the logger.
    :param level: The logging level.
    :param appenders: A list of BaseAppender instances to handle log output.
    :return: An instance of Logger with a CompositeAppender.
    """
    from appenders.composite_appender import CompositeAppender

    composite = CompositeAppender(appenders=appenders)
    return LoggerFactory.create_simple_logger(name, level, [composite])
