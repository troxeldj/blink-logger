from filters import KeywordFilter, LevelFilter

def StringToFilter(value: str) -> type:
    match(value.lower().strip()):
        case 'keyword':
            return KeywordFilter
        case 'level':
            return LevelFilter
        case _:
          raise ValueError(f"Unknown filter type {value}")


def StringToAppender(value: str) -> type:
    """
    Converts a string to an Appender instance.
    """
    match(value.lower().strip()):
        case "console":
            from appenders.console_appender import ConsoleAppender
            return ConsoleAppender
        case "file":
            from appenders.file_appender import FileAppender
            return FileAppender
        case _:
          raise ValueError(f"Unknown appender type: {value}")