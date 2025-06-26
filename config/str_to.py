


def StringToAppender(value: str):
    """
    Converts a string to an Appender instance.
    """
    match(value.lower().strip()):
        case "console":
            from appenders.console_appender import ConsoleAppender
            return ConsoleAppender()
        case "file":
            from appenders.file_appender import FileAppender
            return FileAppender()
        