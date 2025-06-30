from filters import KeywordFilter, LevelFilter


def StringToFilter(value: str) -> type:
  match (value.lower().strip()):
    case "keyword":
      return KeywordFilter
    case "KeywordFilter":
      return KeywordFilter
    case "level":
      return LevelFilter
    case "LevelFilter":
      return LevelFilter
    case _:
      raise ValueError(f"Unknown filter type {value}")


def StringToAppender(value: str) -> type:
  """
  Converts a string to an Appender instance.
  """
  match (value.lower().strip()):
    case "console":
      from appenders.console_appender import ConsoleAppender

      return ConsoleAppender
    case "ConsoleAppender":
      from appenders.console_appender import ConsoleAppender

      return ConsoleAppender
    case "coloredconsole":
      from appenders.console_appender import ColoredConsoleAppender

      return ColoredConsoleAppender
    case "ColoredConsoleAppender":
      from appenders.console_appender import ColoredConsoleAppender

      return ColoredConsoleAppender
    case "file":
      from appenders.file_appender import FileAppender

      return FileAppender
    case "FileAppender":
      from appenders.file_appender import FileAppender

      return FileAppender
    case "mysql":
      from appenders.mysql_appender import MySQLAppender

      return MySQLAppender
    case "MySQLAppender":
      from appenders.mysql_appender import MySQLAppender

      return MySQLAppender
    case _:
      raise ValueError(f"Unknown appender type: {value}")
